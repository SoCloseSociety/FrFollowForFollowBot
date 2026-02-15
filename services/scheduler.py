import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import queries

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """Start the periodic task scheduler."""

    # Expire old missions every hour
    scheduler.add_job(
        expire_old_missions,
        "interval",
        hours=1,
        id="expire_missions",
        replace_existing=True,
    )

    # Reset broken streaks daily at 00:05 UTC
    scheduler.add_job(
        reset_broken_streaks,
        "cron",
        hour=0,
        minute=5,
        id="reset_streaks",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler() -> None:
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


async def expire_old_missions() -> None:
    """Mark expired missions as 'expired'."""
    try:
        count = await queries.expire_old_missions()
        if count > 0:
            logger.info(f"Expired {count} old missions")
    except Exception as e:
        logger.error(f"Error expiring missions: {e}")


async def reset_broken_streaks() -> None:
    """Reset streaks for users who missed their daily check-in."""
    try:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        await queries.reset_streaks_before_date(yesterday)
        logger.info("Broken streaks reset")
    except Exception as e:
        logger.error(f"Error resetting streaks: {e}")
