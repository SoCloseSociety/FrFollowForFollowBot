from __future__ import annotations
import logging
import random
import uuid
from datetime import timedelta

from config import settings
from database import queries
from utils.helpers import utcnow

logger = logging.getLogger(__name__)


class MissionEngine:
    @staticmethod
    async def generate_mission(user_id: int) -> tuple[list[dict], str] | None:
        """
        Generate a mission of MISSION_SIZE Instagram accounts for the user to follow.
        Returns (targets, batch_id) or None if pool is too small.
        """
        mission_size = settings.mission_size

        # Get IDs the user already follows
        existing_follows = await queries.get_user_following_ids(user_id)

        # Get IDs from user's recent missions (last 7 days)
        recent_targets = await queries.get_recent_mission_target_ids(user_id, days=7)

        # Build exclusion set
        exclude_ids = {user_id} | set(existing_follows) | set(recent_targets)

        # Get eligible pool (over-fetch for randomization)
        pool = await queries.get_follow_pool(
            exclude_ids=exclude_ids,
            limit=mission_size * 5,
        )

        if len(pool) < mission_size:
            return None

        # Get auto-mode users for weighting
        auto_users = await queries.get_active_auto_mode_users()
        auto_ids = {u["id"] for u in auto_users}

        # Weighted random selection - auto-mode users get 3x weight
        weighted_pool = []
        for user in pool:
            weight = 3 if user["id"] in auto_ids else 1
            weighted_pool.extend([user] * weight)

        random.shuffle(weighted_pool)

        selected = []
        selected_ids = set()
        for candidate in weighted_pool:
            if candidate["id"] not in selected_ids:
                selected.append(candidate)
                selected_ids.add(candidate["id"])
            if len(selected) == mission_size:
                break

        if len(selected) < mission_size:
            return None

        # Create mission batch
        batch_id = uuid.uuid4().hex[:8]
        expires_at = (utcnow() + timedelta(hours=24)).isoformat()

        targets = [
            {
                "target_instagram_username": s["instagram_username"],
                "target_user_id": s["id"],
            }
            for s in selected
        ]

        await queries.create_mission_batch(user_id, batch_id, targets, expires_at)

        return targets, batch_id
