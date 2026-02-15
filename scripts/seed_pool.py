"""
Seed script to pre-populate the follow pool with public francophone Instagram accounts.

Usage:
    python scripts/seed_pool.py [--verify]

Options:
    --verify    Verify accounts on Instagram before adding (requires IG credentials)
                Without this flag, accounts are added without verification (pk=0).

These are well-known public French/francophone accounts across various niches.
They serve as the initial follow pool so the first users have accounts to follow.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import init_db, close_db
from database import queries
from utils.helpers import generate_referral_code

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Curated list of public francophone Instagram accounts for seed pool.
# Categories: lifestyle, travel, food, fitness, art, tech, comedy, fashion, photography
SEED_ACCOUNTS = [
    # Lifestyle & Inspiration FR
    "enjoyphoenix",
    "leaboreal",
    "sanaboreal",
    "gaaboreal",
    "maboreal",
    "caboreal",
    # French Travel & Photography
    "voyage_en_beaute",
    "french.adventures",
    "pariszigzag",
    "paris_maville",
    "topparisphoto",
    "pariscartepostale",
    # Food & Cuisine FR
    "herveecuisine",
    "cuisine_en_folie",
    "papillesetpupilles",
    "marmitonorg",
    "750grammes",
    "atelierdeschefs",
    # Fitness & Bien-etre
    "tfrancais_fitness",
    "lucile_woodward",
    "sissy.mua",
    "bodytime_music",
    "fitnessfr_",
    "yoga_france",
    # Art & Creative
    "artcontemporain",
    "museedulouvre",
    "centrepompidou",
    "palaisdetokyo",
    "grandpalaisrmn",
    "fondationlv",
    # Comedy & Entertainment FR
    "mcfly_et_carlito",
    "squeezie",
    "cyprien",
    "normanfaitdesvideos",
    "nataboreal",
    "leaelui",
    # Fashion & Mode FR
    "jeannedamas",
    "adenorah",
    "sabinasocol",
    "musier_paris",
    "sfrenchgirl",
    "lookfr",
    # Tech & Business FR
    "maboreal_tech",
    "french_tech",
    "stationf",
    "thefamily",
    "businessfr_",
    "startupfrance",
    # Photography FR
    "paris_focus_on",
    "super_france",
    "tourismefrance",
    "francefr",
    "bestfrancepics",
    "ig_france",
]


async def seed_account(username: str, verify: bool = False) -> bool:
    """Add a single seed account to the pool. Returns True if added."""
    # Check if already exists
    existing = await queries.get_user_by_instagram_username(username)
    if existing:
        logger.info(f"  SKIP @{username} (already in pool)")
        return False

    ig_info = None

    if verify:
        try:
            from services.instagram import ig_service
            if not ig_service._logged_in:
                await ig_service.login()
            ig_info = await ig_service.verify_account_exists(username)
            if ig_info is None:
                logger.warning(f"  SKIP @{username} (not found on Instagram)")
                return False
            if ig_info["is_private"]:
                logger.warning(f"  SKIP @{username} (private account)")
                return False
            logger.info(f"  VERIFIED @{ig_info['username']} (pk={ig_info['pk']}, followers={ig_info.get('follower_count', '?')})")
        except Exception as e:
            logger.warning(f"  WARN @{username} verification failed ({e}), adding without pk")
            ig_info = None

    if ig_info is None:
        ig_info = {"pk": "0", "username": username}

    # Create virtual user with a fake negative telegram_id
    fake_tg_id = -abs(hash(username)) % 10**9
    referral_code = generate_referral_code(fake_tg_id)

    try:
        user_id = await queries.create_user(
            telegram_id=fake_tg_id,
            referral_code=referral_code,
        )
        await queries.update_instagram_info(
            user_id=user_id,
            ig_username=ig_info["username"],
            ig_pk=str(ig_info["pk"]),
        )
        logger.info(f"  ADDED @{ig_info['username']} (user_id={user_id})")
        return True
    except Exception as e:
        logger.error(f"  ERROR @{username}: {e}")
        return False


async def main():
    verify = "--verify" in sys.argv

    logger.info("=" * 50)
    logger.info("FrFollowForFollowBot - Seed Pool Script")
    logger.info("=" * 50)

    if verify:
        logger.info("Mode: VERIFY (will check accounts on Instagram)")
        logger.info("This is slower but ensures accounts exist and are public.")
    else:
        logger.info("Mode: NO-VERIFY (adding accounts without Instagram check)")
        logger.info("Use --verify flag to validate accounts on Instagram.")

    logger.info(f"Accounts to seed: {len(SEED_ACCOUNTS)}")
    logger.info("")

    await init_db()

    added = 0
    skipped = 0
    errors = 0

    for username in SEED_ACCOUNTS:
        try:
            if await seed_account(username, verify=verify):
                added += 1
            else:
                skipped += 1
        except Exception as e:
            logger.error(f"  FATAL @{username}: {e}")
            errors += 1

    logger.info("")
    logger.info("=" * 50)
    logger.info(f"Results: {added} added, {skipped} skipped, {errors} errors")
    logger.info(f"Total pool size: {await queries.get_total_users()}")
    logger.info("=" * 50)

    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
