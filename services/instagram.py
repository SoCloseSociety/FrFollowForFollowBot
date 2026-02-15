from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from collections import deque
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)

_SESSION_PATH = Path("data/ig_session.json")


class InstagramRateLimiter:
    """
    Ensures safe Instagram API usage:
    - Only 1 concurrent call at a time (semaphore)
    - Random delay between calls (human-like)
    - Hourly call tracking with auto-throttle
    - Exponential backoff on errors
    """

    def __init__(self, min_delay: int = 5, max_delay: int = 15, max_per_hour: int = 60):
        self._semaphore = asyncio.Semaphore(1)
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._max_per_hour = max_per_hour
        self._call_timestamps: deque[float] = deque()
        self._backoff_until: float = 0
        self._consecutive_errors: int = 0

    def _prune_old_timestamps(self) -> None:
        cutoff = time.time() - 3600
        while self._call_timestamps and self._call_timestamps[0] < cutoff:
            self._call_timestamps.popleft()

    @property
    def calls_this_hour(self) -> int:
        self._prune_old_timestamps()
        return len(self._call_timestamps)

    @property
    def is_throttled(self) -> bool:
        return self.calls_this_hour >= self._max_per_hour

    async def acquire(self) -> None:
        await self._semaphore.acquire()

        # Wait for backoff if needed
        now = time.time()
        if self._backoff_until > now:
            wait = self._backoff_until - now
            logger.warning(f"Instagram backoff: waiting {wait:.0f}s")
            await asyncio.sleep(wait)

        # Check hourly limit
        self._prune_old_timestamps()
        if self.is_throttled:
            wait = 3600 - (time.time() - self._call_timestamps[0]) + 10
            logger.warning(f"Instagram hourly limit reached ({self._max_per_hour}). Waiting {wait:.0f}s")
            await asyncio.sleep(max(wait, 60))

    async def release(self, error: bool = False) -> None:
        self._call_timestamps.append(time.time())

        if error:
            self._consecutive_errors += 1
            backoff = min(300, (2 ** self._consecutive_errors) * 5 + random.uniform(0, 10))
            self._backoff_until = time.time() + backoff
            logger.warning(f"Instagram error #{self._consecutive_errors}, backoff {backoff:.0f}s")
        else:
            self._consecutive_errors = 0
            self._backoff_until = 0

        # Human-like delay between calls
        delay = random.uniform(self._min_delay, self._max_delay)
        # Add jitter based on time of day for more human-like pattern
        hour = time.localtime().tm_hour
        if 2 <= hour <= 6:
            delay *= 1.5  # Slower at night
        await asyncio.sleep(delay)

        self._semaphore.release()


class InstagramService:
    """
    Wraps instagrapi.Client for Instagram scraping.
    All methods are async-safe via asyncio.to_thread().
    Features:
    - Session persistence (avoid re-logins)
    - Rate limiting with hourly caps
    - Exponential backoff on errors
    - Automatic re-login on auth failures
    - Retry logic with configurable attempts
    """

    def __init__(self):
        self._client = None
        self._rate_limiter = InstagramRateLimiter(
            min_delay=settings.instagram_request_delay_min,
            max_delay=settings.instagram_request_delay_max,
            max_per_hour=settings.max_verifications_per_hour * 3,
        )
        self._logged_in = False
        self._login_lock = asyncio.Lock()
        self._last_login_attempt: float = 0

    @property
    def is_available(self) -> bool:
        return self._logged_in and not self._rate_limiter.is_throttled

    @property
    def calls_this_hour(self) -> int:
        return self._rate_limiter.calls_this_hour

    async def login(self) -> None:
        """Login to Instagram or restore session."""
        async with self._login_lock:
            # Avoid rapid re-login attempts
            if time.time() - self._last_login_attempt < 30:
                logger.warning("Login attempt too soon, skipping")
                return
            self._last_login_attempt = time.time()

            from instagrapi import Client

            self._client = Client()
            self._client.delay_range = [2, 5]

            if settings.instagram_proxy:
                self._client.set_proxy(settings.instagram_proxy)

            _SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Try to restore session first
            if _SESSION_PATH.exists():
                try:
                    session_data = json.loads(_SESSION_PATH.read_text())
                    self._client.set_settings(session_data)
                    await asyncio.to_thread(
                        self._client.login,
                        settings.instagram_username,
                        settings.instagram_password,
                    )
                    self._save_session()
                    self._logged_in = True
                    logger.info("Instagram session restored successfully")
                    return
                except Exception as e:
                    logger.warning(f"Session restore failed: {e}")
                    # Reset client for fresh login
                    self._client = Client()
                    self._client.delay_range = [2, 5]
                    if settings.instagram_proxy:
                        self._client.set_proxy(settings.instagram_proxy)

            # Fresh login
            try:
                await asyncio.to_thread(
                    self._client.login,
                    settings.instagram_username,
                    settings.instagram_password,
                )
                self._save_session()
                self._logged_in = True
                logger.info("Instagram fresh login successful")
            except Exception as e:
                logger.error(f"Instagram login failed: {e}")
                self._logged_in = False
                raise

    def _save_session(self) -> None:
        """Persist session to avoid re-login."""
        if self._client is None:
            return
        try:
            session_data = self._client.get_settings()
            _SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
            _SESSION_PATH.write_text(json.dumps(session_data, default=str))
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    async def _safe_call(self, func, *args, max_retries: int = 2):
        """
        Execute an Instagram API call with:
        - Rate limiting
        - Retry on transient errors
        - Auth error recovery
        - Exponential backoff
        """
        if not self._logged_in:
            raise RuntimeError("Instagram service not logged in")

        last_error = None
        for attempt in range(max_retries + 1):
            had_error = False
            try:
                await self._rate_limiter.acquire()
                try:
                    result = await asyncio.to_thread(func, *args)
                    await self._rate_limiter.release(error=False)
                    # Periodically save session
                    if random.random() < 0.1:
                        self._save_session()
                    return result
                except Exception as e:
                    had_error = True
                    await self._rate_limiter.release(error=True)
                    raise
            except Exception as e:
                last_error = e
                error_name = type(e).__name__

                # Handle auth errors
                if error_name in ("LoginRequired", "ChallengeRequired", "PleaseWaitFewMinutes"):
                    logger.warning(f"Instagram auth/rate error: {error_name}")
                    if attempt < max_retries:
                        try:
                            await self._handle_auth_error()
                        except Exception:
                            pass
                        await asyncio.sleep(random.uniform(30, 60))
                        continue
                    raise

                # User not found is not retryable
                if error_name in ("UserNotFound", "ClientNotFoundError"):
                    raise

                # Transient errors - retry
                if attempt < max_retries:
                    wait = (2 ** attempt) * 10 + random.uniform(0, 5)
                    logger.warning(f"Instagram transient error (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {wait:.0f}s")
                    await asyncio.sleep(wait)
                    continue

                raise

        raise last_error

    async def verify_account_exists(self, username: str) -> dict | None:
        """
        Check if an Instagram account exists.
        Returns dict with: pk, username, full_name, is_private, follower_count
        Returns None if not found.
        """
        try:
            user_info = await self._safe_call(
                self._client.user_info_by_username, username
            )
            return {
                "pk": str(user_info.pk),
                "username": user_info.username,
                "full_name": user_info.full_name,
                "is_private": user_info.is_private,
                "follower_count": user_info.follower_count,
            }
        except Exception as e:
            error_name = type(e).__name__
            if error_name in ("UserNotFound", "ClientNotFoundError"):
                return None
            logger.error(f"verify_account_exists(@{username}): {e}")
            raise

    async def check_follow(self, follower_ig_pk: str, target_username: str) -> bool:
        """
        Check if follower_ig_pk follows target_username.
        Strategy: get target's followers list and check if follower is present.
        Limited to 200 recent followers for speed/safety.
        """
        try:
            # Validate pk format
            try:
                follower_pk_int = int(follower_ig_pk)
            except (ValueError, TypeError):
                logger.error(f"Invalid follower_ig_pk: {follower_ig_pk}")
                return False

            # Get target's PK
            target_info = await self._safe_call(
                self._client.user_info_by_username, target_username
            )
            target_pk = target_info.pk

            # Get target's followers (limited to 200 for safety)
            followers = await self._safe_call(
                self._client.user_followers, target_pk, 200
            )

            # followers is a dict {pk: UserShort, ...}
            return follower_pk_int in followers

        except Exception as e:
            error_name = type(e).__name__
            if error_name in ("UserNotFound", "ClientNotFoundError"):
                return False
            logger.error(f"check_follow({follower_ig_pk} -> @{target_username}): {e}")
            raise

    async def _handle_auth_error(self) -> None:
        """Handle authentication errors by re-logging in."""
        async with self._login_lock:
            logger.warning("Instagram auth error, attempting re-login...")
            try:
                if self._client is None:
                    return
                await asyncio.to_thread(
                    self._client.login,
                    settings.instagram_username,
                    settings.instagram_password,
                )
                self._save_session()
                self._logged_in = True
                logger.info("Instagram re-login successful")
            except Exception as e:
                logger.error(f"Instagram re-login failed: {e}")
                self._logged_in = False


# Module-level singleton
ig_service = InstagramService()
