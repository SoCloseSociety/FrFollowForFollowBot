from __future__ import annotations

import logging
from datetime import timedelta

from database.db import get_db
from utils.helpers import utcnow

logger = logging.getLogger(__name__)


def _row_to_dict(row) -> dict | None:
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(r) for r in rows]


# ══════════════════════════════════════════
# USER OPERATIONS
# ══════════════════════════════════════════

async def create_user(
    telegram_id: int,
    referral_code: str,
    telegram_username: str | None = None,
    referrer_id: int | None = None,
) -> int:
    db = await get_db()
    cursor = await db.execute(
        """
        INSERT INTO users (telegram_id, telegram_username, referral_code, referrer_id)
        VALUES (?, ?, ?, ?)
        """,
        (telegram_id, telegram_username, referral_code, referrer_id),
    )
    await db.commit()
    return cursor.lastrowid


async def get_user_by_telegram_id(telegram_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
    )
    return _row_to_dict(await cursor.fetchone())


async def get_user_by_id(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return _row_to_dict(await cursor.fetchone())


async def get_user_by_referral_code(code: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE referral_code = ?", (code,)
    )
    return _row_to_dict(await cursor.fetchone())


async def get_user_by_instagram_username(username: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE instagram_username = ? COLLATE NOCASE", (username,)
    )
    return _row_to_dict(await cursor.fetchone())


async def update_instagram_info(
    user_id: int, ig_username: str, ig_pk: str
) -> None:
    db = await get_db()
    await db.execute(
        """
        UPDATE users
        SET instagram_username = ?, instagram_user_pk = ?,
            is_registered = 1, updated_at = datetime('now')
        WHERE id = ?
        """,
        (ig_username, ig_pk, user_id),
    )
    await db.commit()


async def update_etoiles(user_id: int, delta: int) -> int:
    db = await get_db()
    await db.execute(
        """
        UPDATE users
        SET etoiles = CASE
            WHEN etoiles + ? < 0 THEN 0
            ELSE etoiles + ?
        END,
        updated_at = datetime('now')
        WHERE id = ?
        """,
        (delta, delta, user_id),
    )
    await db.commit()
    cursor = await db.execute("SELECT etoiles FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    return row["etoiles"] if row else 0


async def update_level(user_id: int, level: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET level = ?, updated_at = datetime('now') WHERE id = ?",
        (level, user_id),
    )
    await db.commit()


async def update_streak(user_id: int, streak: int) -> None:
    db = await get_db()
    await db.execute(
        """
        UPDATE users
        SET current_streak = ?,
            longest_streak = CASE
                WHEN ? > longest_streak THEN ? ELSE longest_streak
            END,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (streak, streak, streak, user_id),
    )
    await db.commit()


async def set_auto_mode(user_id: int, until: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET auto_mode_until = ?, updated_at = datetime('now') WHERE id = ?",
        (until, user_id),
    )
    await db.commit()


async def get_active_auto_mode_users() -> list[dict]:
    db = await get_db()
    now = utcnow().isoformat()
    cursor = await db.execute(
        """
        SELECT * FROM users
        WHERE auto_mode_until IS NOT NULL AND auto_mode_until > ?
          AND is_registered = 1 AND is_banned = 0
        """,
        (now,),
    )
    return _rows_to_dicts(await cursor.fetchall())


async def mark_registered(user_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET is_registered = 1, updated_at = datetime('now') WHERE id = ?",
        (user_id,),
    )
    await db.commit()


async def increment_follows_given(user_id: int) -> None:
    db = await get_db()
    await db.execute(
        """
        UPDATE users SET total_follows_given = total_follows_given + 1,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (user_id,),
    )
    await db.commit()


async def increment_follows_received(user_id: int) -> None:
    db = await get_db()
    await db.execute(
        """
        UPDATE users SET total_follows_received = total_follows_received + 1,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (user_id,),
    )
    await db.commit()


async def update_last_verification(user_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET last_verification_at = datetime('now'), updated_at = datetime('now') WHERE id = ?",
        (user_id,),
    )
    await db.commit()


async def set_user_banned(user_id: int, banned: bool) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET is_banned = ?, updated_at = datetime('now') WHERE id = ?",
        (1 if banned else 0, user_id),
    )
    await db.commit()


async def update_telegram_username(user_id: int, username: str | None) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET telegram_username = ?, updated_at = datetime('now') WHERE id = ?",
        (username, user_id),
    )
    await db.commit()


async def update_notifications(user_id: int, enabled: bool) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET notifications_enabled = ?, updated_at = datetime('now') WHERE id = ?",
        (1 if enabled else 0, user_id),
    )
    await db.commit()


async def set_referrer(user_id: int, referrer_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET referrer_id = ?, updated_at = datetime('now') WHERE id = ?",
        (referrer_id, user_id),
    )
    await db.commit()


async def delete_user(user_id: int) -> None:
    db = await get_db()
    await db.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
    await db.execute("DELETE FROM daily_checkins WHERE user_id = ?", (user_id,))
    await db.execute("DELETE FROM missions WHERE user_id = ?", (user_id,))
    await db.execute(
        "DELETE FROM follows WHERE follower_user_id = ? OR followed_user_id = ?",
        (user_id, user_id),
    )
    await db.execute(
        "DELETE FROM referrals WHERE referrer_id = ? OR referred_id = ?",
        (user_id, user_id),
    )
    await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    await db.commit()


async def get_total_users() -> int:
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as cnt FROM users WHERE is_registered = 1")
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


# ══════════════════════════════════════════
# MISSION OPERATIONS
# ══════════════════════════════════════════

async def create_mission_batch(
    user_id: int,
    batch_id: str,
    targets: list[dict],
    expires_at: str,
) -> None:
    db = await get_db()
    for t in targets:
        await db.execute(
            """
            INSERT INTO missions (user_id, batch_id, target_instagram_username, target_user_id, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, batch_id, t["target_instagram_username"], t.get("target_user_id"), expires_at),
        )
    await db.commit()


async def get_active_mission_batch(user_id: int) -> list[dict] | None:
    db = await get_db()
    now = utcnow().isoformat()
    # Get the most recent batch that has pending missions
    cursor = await db.execute(
        """
        SELECT batch_id FROM missions
        WHERE user_id = ? AND status = 'pending' AND expires_at > ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id, now),
    )
    batch_row = await cursor.fetchone()
    if not batch_row:
        return None
    batch_id = batch_row["batch_id"]
    # Get all missions in this batch (including already verified ones)
    cursor = await db.execute(
        """
        SELECT * FROM missions
        WHERE user_id = ? AND batch_id = ?
        ORDER BY id
        """,
        (user_id, batch_id),
    )
    rows = _rows_to_dicts(await cursor.fetchall())
    return rows if rows else None


async def get_missions_by_batch(batch_id: str) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM missions WHERE batch_id = ? ORDER BY id", (batch_id,)
    )
    return _rows_to_dicts(await cursor.fetchall())


async def update_mission_status(mission_id: int, status: str) -> None:
    db = await get_db()
    verified_at = utcnow().isoformat() if status == "verified" else None
    await db.execute(
        "UPDATE missions SET status = ?, verified_at = ? WHERE id = ?",
        (status, verified_at, mission_id),
    )
    await db.commit()


async def expire_old_missions() -> int:
    db = await get_db()
    now = utcnow().isoformat()
    cursor = await db.execute(
        """
        UPDATE missions SET status = 'expired'
        WHERE status = 'pending' AND expires_at <= ?
        """,
        (now,),
    )
    await db.commit()
    return cursor.rowcount


async def get_completed_mission_count(user_id: int) -> int:
    """Count distinct batches where ALL missions are verified."""
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT COUNT(*) as cnt FROM (
            SELECT batch_id
            FROM missions
            WHERE user_id = ?
            GROUP BY batch_id
            HAVING COUNT(*) = SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END)
        )
        """,
        (user_id,),
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


async def get_recent_mission_target_ids(user_id: int, days: int = 7) -> list[int]:
    db = await get_db()
    since = (utcnow() - timedelta(days=days)).isoformat()
    cursor = await db.execute(
        """
        SELECT DISTINCT target_user_id FROM missions
        WHERE user_id = ? AND target_user_id IS NOT NULL AND created_at > ?
        """,
        (user_id, since),
    )
    return [r["target_user_id"] for r in await cursor.fetchall()]


# ══════════════════════════════════════════
# FOLLOW OPERATIONS
# ══════════════════════════════════════════

async def record_follow(
    follower_id: int, followed_id: int, mission_id: int | None = None
) -> None:
    db = await get_db()
    await db.execute(
        """
        INSERT OR IGNORE INTO follows (follower_user_id, followed_user_id, mission_id, verified, verified_at)
        VALUES (?, ?, ?, 1, datetime('now'))
        """,
        (follower_id, followed_id, mission_id),
    )
    await db.commit()


async def get_user_following_ids(user_id: int) -> list[int]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT followed_user_id FROM follows WHERE follower_user_id = ?",
        (user_id,),
    )
    return [r["followed_user_id"] for r in await cursor.fetchall()]


async def get_follow_pool(exclude_ids: set[int], limit: int = 25) -> list[dict]:
    db = await get_db()
    if not exclude_ids:
        exclude_ids = {-1}
    # Cap the exclude list to prevent oversized queries
    exclude_list = list(exclude_ids)[:500]
    placeholders = ",".join("?" for _ in exclude_list)
    cursor = await db.execute(
        f"""
        SELECT id, instagram_username, instagram_user_pk, auto_mode_until
        FROM users
        WHERE is_registered = 1 AND is_banned = 0
          AND id NOT IN ({placeholders})
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (*exclude_list, limit),
    )
    return _rows_to_dicts(await cursor.fetchall())


# ══════════════════════════════════════════
# REFERRAL OPERATIONS
# ══════════════════════════════════════════

async def create_referral(referrer_id: int, referred_id: int) -> None:
    db = await get_db()
    await db.execute(
        """
        INSERT OR IGNORE INTO referrals (referrer_id, referred_id, signup_bonus_claimed)
        VALUES (?, ?, 1)
        """,
        (referrer_id, referred_id),
    )
    await db.commit()


async def get_referral_by_users(referrer_id: int, referred_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM referrals WHERE referrer_id = ? AND referred_id = ?",
        (referrer_id, referred_id),
    )
    return _row_to_dict(await cursor.fetchone())


async def claim_mission_bonus(referral_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE referrals SET mission_bonus_claimed = 1 WHERE id = ?",
        (referral_id,),
    )
    await db.commit()


async def get_referral_stats(user_id: int) -> dict:
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    count = row["count"] if row else 0

    cursor = await db.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN signup_bonus_claimed = 1 THEN 1 ELSE 0 END), 0) * ? +
            COALESCE(SUM(CASE WHEN mission_bonus_claimed = 1 THEN 1 ELSE 0 END), 0) * ?
        as earned
        FROM referrals WHERE referrer_id = ?
        """,
        (10, 5, user_id),
    )
    row2 = await cursor.fetchone()
    earned = row2["earned"] if row2 and row2["earned"] else 0

    return {"count": count, "earned": earned}


async def get_referral_leaderboard(limit: int = 10) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT u.telegram_username, u.instagram_username, COUNT(r.id) as referral_count
        FROM referrals r
        JOIN users u ON u.id = r.referrer_id
        GROUP BY r.referrer_id
        ORDER BY referral_count DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _rows_to_dicts(await cursor.fetchall())


# ══════════════════════════════════════════
# ACHIEVEMENT OPERATIONS
# ══════════════════════════════════════════

async def grant_achievement(user_id: int, achievement_type: str) -> bool:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO achievements (user_id, achievement_type) VALUES (?, ?)",
            (user_id, achievement_type),
        )
        await db.commit()
        return True
    except Exception:
        return False


async def get_user_achievements(user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM achievements WHERE user_id = ? ORDER BY earned_at",
        (user_id,),
    )
    return _rows_to_dicts(await cursor.fetchall())


# ══════════════════════════════════════════
# DAILY CHECKIN OPERATIONS
# ══════════════════════════════════════════

async def record_daily_checkin(
    user_id: int, checkin_date: str, streak: int, etoiles: int
) -> None:
    db = await get_db()
    await db.execute(
        """
        INSERT OR IGNORE INTO daily_checkins (user_id, checkin_date, streak_count, etoiles_awarded)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, checkin_date, streak, etoiles),
    )
    await db.execute(
        "UPDATE users SET last_daily_checkin = ?, updated_at = datetime('now') WHERE id = ?",
        (checkin_date, user_id),
    )
    await db.commit()


async def get_last_checkin(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM daily_checkins
        WHERE user_id = ?
        ORDER BY checkin_date DESC
        LIMIT 1
        """,
        (user_id,),
    )
    return _row_to_dict(await cursor.fetchone())


async def reset_streaks_before_date(date_str: str) -> None:
    db = await get_db()
    await db.execute(
        """
        UPDATE users SET current_streak = 0, updated_at = datetime('now')
        WHERE last_daily_checkin IS NOT NULL AND last_daily_checkin < ?
          AND current_streak > 0
        """,
        (date_str,),
    )
    await db.commit()


# ══════════════════════════════════════════
# LEADERBOARD OPERATIONS
# ══════════════════════════════════════════

async def get_etoiles_leaderboard(limit: int = 10) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT id, telegram_username, instagram_username, etoiles, level
        FROM users
        WHERE is_registered = 1 AND is_banned = 0
        ORDER BY etoiles DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _rows_to_dicts(await cursor.fetchall())


async def get_follows_leaderboard(limit: int = 10) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT id, telegram_username, instagram_username, total_follows_given, level
        FROM users
        WHERE is_registered = 1 AND is_banned = 0
        ORDER BY total_follows_given DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _rows_to_dicts(await cursor.fetchall())


async def get_active_missions_count() -> int:
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM missions WHERE status = 'pending' AND expires_at > datetime('now')"
    )
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


async def get_total_verified_follows() -> int:
    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as cnt FROM follows WHERE verified = 1")
    row = await cursor.fetchone()
    return row["cnt"] if row else 0


async def get_user_rank(user_id: int) -> int:
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT COUNT(*) + 1 as rank FROM users
        WHERE is_registered = 1 AND is_banned = 0
          AND etoiles > (SELECT COALESCE(etoiles, 0) FROM users WHERE id = ?)
        """,
        (user_id,),
    )
    row = await cursor.fetchone()
    return row["rank"] if row else 0
