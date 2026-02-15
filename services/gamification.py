from __future__ import annotations
import logging
from datetime import date, timedelta

from config import settings
from database import queries
from utils.texts import Texts

logger = logging.getLogger(__name__)

LEVEL_THRESHOLDS = [
    ("Debutant", 0),
    ("Explorateur", 51),
    ("Influenceur", 201),
    ("Star", 501),
    ("Legende", 1001),
]


def compute_level(etoiles: int) -> str:
    """Determine level based on total Etoiles."""
    level = "Debutant"
    for name, threshold in LEVEL_THRESHOLDS:
        if etoiles >= threshold:
            level = name
    return level


async def award_etoiles(user_id: int, amount: int, reason: str) -> dict:
    """
    Award (or deduct) Etoiles and handle level-ups + achievements.
    Returns dict:
      - new_total: int
      - leveled_up: bool
      - new_level: str | None
      - achievements_unlocked: list[str]
    """
    new_total = await queries.update_etoiles(user_id, amount)
    new_level = compute_level(new_total)

    user = await queries.get_user_by_id(user_id)
    if user is None:
        return {"new_total": new_total, "leveled_up": False, "new_level": None, "achievements_unlocked": []}

    old_level = user["level"]
    leveled_up = new_level != old_level

    if leveled_up:
        await queries.update_level(user_id, new_level)

    achievements = await _check_achievements(user_id, user, new_total)

    return {
        "new_total": new_total,
        "leveled_up": leveled_up,
        "new_level": new_level if leveled_up else None,
        "achievements_unlocked": achievements,
    }


async def _check_achievements(user_id: int, user: dict, etoiles: int) -> list[str]:
    """Check and grant new achievements based on current state."""
    unlocked = []

    # Follow milestones
    total_given = user["total_follows_given"]
    follow_achievements = [
        (1, "first_follow"),
        (10, "ten_follows"),
        (50, "fifty_follows"),
        (100, "hundred_follows"),
    ]
    for threshold, achievement in follow_achievements:
        if total_given >= threshold:
            if await queries.grant_achievement(user_id, achievement):
                unlocked.append(achievement)

    # Level achievements
    level = compute_level(etoiles)
    level_achievements = {
        "Explorateur": "level_explorateur",
        "Influenceur": "level_influenceur",
        "Star": "level_star",
        "Legende": "level_legende",
    }
    if level in level_achievements:
        ach = level_achievements[level]
        if await queries.grant_achievement(user_id, ach):
            unlocked.append(ach)

    # Streak achievements
    streak = user["current_streak"]
    streak_achievements = [(7, "streak_7"), (30, "streak_30")]
    for threshold, achievement in streak_achievements:
        if streak >= threshold:
            if await queries.grant_achievement(user_id, achievement):
                unlocked.append(achievement)

    return unlocked


async def process_daily_checkin(user_id: int) -> dict | None:
    """
    Process daily check-in.
    Returns None if already checked in today.
    Returns dict: etoiles_awarded, streak_count, streak_bonus.
    """
    today = date.today().isoformat()
    last = await queries.get_last_checkin(user_id)

    if last and last["checkin_date"] == today:
        return None

    # Calculate streak
    if last:
        try:
            last_date = date.fromisoformat(last["checkin_date"])
            if (date.today() - last_date).days == 1:
                new_streak = last["streak_count"] + 1
            else:
                new_streak = 1
        except ValueError:
            new_streak = 1
    else:
        new_streak = 1

    etoiles = settings.etoiles_daily_login
    streak_bonus = 0

    # 7-day streak bonus
    if new_streak > 0 and new_streak % 7 == 0:
        streak_bonus = settings.etoiles_streak_7_days

    total_etoiles = etoiles + streak_bonus

    await queries.record_daily_checkin(user_id, today, new_streak, total_etoiles)
    await queries.update_streak(user_id, new_streak)
    await queries.update_etoiles(user_id, total_etoiles)

    # Check streak achievements
    user = await queries.get_user_by_id(user_id)
    if user:
        await _check_achievements(user_id, user, user["etoiles"])

    return {
        "etoiles_awarded": etoiles,
        "streak_count": new_streak,
        "streak_bonus": streak_bonus,
    }


async def process_referral_signup(referrer_id: int, referred_id: int) -> None:
    """Called when a new user signs up via referral link."""
    await queries.create_referral(referrer_id, referred_id)
    await award_etoiles(referrer_id, settings.etoiles_per_referral, "referral_signup")

    # Update referrer_id on the referred user
    await queries.set_referrer(referred_id, referrer_id)

    # Check referral achievements
    stats = await queries.get_referral_stats(referrer_id)
    if stats["count"] >= 1:
        await queries.grant_achievement(referrer_id, "first_referral")
    if stats["count"] >= 5:
        await queries.grant_achievement(referrer_id, "five_referrals")


async def process_referral_first_mission(referred_id: int) -> None:
    """Called when a referred user completes their first mission."""
    user = await queries.get_user_by_id(referred_id)
    if not user or not user["referrer_id"]:
        return

    referral = await queries.get_referral_by_users(user["referrer_id"], referred_id)
    if referral and not referral["mission_bonus_claimed"]:
        await queries.claim_mission_bonus(referral["id"])
        await award_etoiles(
            user["referrer_id"],
            settings.etoiles_referral_first_mission,
            "referral_first_mission",
        )
