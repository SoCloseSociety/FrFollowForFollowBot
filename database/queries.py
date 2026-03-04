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
        ""\"
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
        ""\"
        SELECT * FROM users WHERE telegram_id = ?
        """,
        (telegram_id,),
    )
    return _row_to_dict(await cursor.fetchone())

async def get_user_by_id(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM users WHERE id = ?
        """,
        (user_id,),
    )
    return _row_to_dict(await cursor.fetchone())

async def get_user_by_referral_code(code: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM users WHERE referral_code = ?
        """,
        (code,),
    )
    return _row_to_dict(await cursor.fetchone())

async def get_user_by_instagram_username(username: str) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM users WHERE instagram_username = ? COLLATE NOCASE
        """,
        (username,),
    )
    return _row_to_dict(await cursor.fetchone())

async def update_instagram_info(
    user_id: int, ig_username: str, ig_pk: str
) -> None:
    db = await get_db()
    await db.execute(
        ""\"
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
        ""\"
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
    cursor = await db.execute(""\"
    SELECT etoiles FROM users WHERE id = ?
    """, (user_id,))
    row = await cursor.fetchone()
    return row["etoiles"] if row else 0

async def update_level(user_id: int, level: str) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE users SET level = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (level, user_id),
    )
    await db.commit()

async def update_streak(user_id: int, streak: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
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
        ""\"
        UPDATE users SET auto_mode_until = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (until, user_id),
    )
    await db.commit()

async def get_active_auto_mode_users() -> list[dict]:
    db = await get_db()
    now = utcnow().isoformat()
    cursor = await db.execute(
        ""\"
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
        ""\"
        UPDATE users SET is_registered = 1, updated_at = datetime('now') WHERE id = ?
        """,
        (user_id,),
    )
    await db.commit()

async def increment_follows_given(user_id: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
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
        ""\"
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
        ""\"
        UPDATE users SET last_verification_at = datetime('now'), updated_at = datetime('now') WHERE id = ?
        """,
        (user_id,),
    )
    await db.commit()

async def set_user_banned(user_id: int, banned: bool) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE users SET is_banned = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (1 if banned else 0, user_id),
    )
    await db.commit()

async def update_telegram_username(user_id: int, username: str | None) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE users SET telegram_username = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (username, user_id),
    )
    await db.commit()

async def update_notifications(user_id: int, enabled: bool) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE users SET notifications_enabled = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (1 if enabled else 0, user_id),
    )
    await db.commit()

async def set_referrer(user_id: int, referrer_id: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE users SET referrer_id = ?, updated_at = datetime('now') WHERE id = ?
        """,
        (referrer_id, user_id),
    )
    await db.commit()

async def delete_user(user_id: int) -> None:
    db = await get_db()
    await db.execute(""\"
    DELETE FROM achievements WHERE user_id = ?
    """, (user_id,))
    await db.execute(""\"
    DELETE FROM daily_checkins WHERE user_id = ?
    """, (user_id,))
    await db.execute(""\"
    DELETE FROM missions WHERE user_id = ?
    """, (user_id,))
    await db.execute(
        ""\"
        DELETE FROM follows WHERE follower_user_id = ? OR followed_user_id = ?
        """,
        (user_id, user_id),
    )
    await db.execute(
        ""\"
        DELETE FROM referrals WHERE referrer_id = ? OR referred_id = ?
        """,
        (user_id, user_id),
    )
    await db.execute(""\"
    DELETE FROM users WHERE id = ?
    """, (user_id,))
    await db.commit()

async def get_total_users() -> int:
    db = await get_db()
    cursor = await db.execute(""\"
    SELECT COUNT(*) as cnt FROM users WHERE is_registered = 1
    """)
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
            ""\"
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
        ""\"
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

    # Get all missions for the batch
    cursor = await db.execute(
        ""\"
        SELECT * FROM missions WHERE batch_id = ? AND status = 'pending'
        """,
        (batch_row["batch_id"],),
    )
    return _rows_to_dicts(await cursor.fetchall())

async def complete_mission(user_id: int, mission_id: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE missions SET status = 'completed', verified_at = datetime('now') WHERE id = ? AND user_id = ?
        """,
        (mission_id, user_id),
    )
    await db.commit()

async def get_user_missions(user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM missions WHERE user_id = ? ORDER BY created_at DESC
        """,
        (user_id,),
    )
    return _rows_to_dicts(await cursor.fetchall())

async def get_mission_by_id(mission_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM missions WHERE id = ?
        """,
        (mission_id,),
    )
    return _row_to_dict(await cursor.fetchone())

async def update_mission_target(user_id: int, mission_id: int, target_username: str) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE missions SET target_instagram_username = ? WHERE id = ? AND user_id = ?
        """,
        (target_username, mission_id, user_id),
    )
    await db.commit()

async def delete_mission(mission_id: int) -> None:
    db = await get_db()
    await db.execute(""\"
    DELETE FROM missions WHERE id = ?
    """, (mission_id,))
    await db.commit()

# ══════════════════════════════════════════
# FOLLOW OPERATIONS
# ══════════════════════════════════════════

async def create_follow(
    follower_user_id: int,
    followed_user_id: int,
    mission_id: int | None = None,
) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        INSERT INTO follows (follower_user_id, followed_user_id, mission_id)
        VALUES (?, ?, ?)
        """,
        (follower_user_id, followed_user_id, mission_id),
    )
    await db.commit()

async def get_follows_by_follower(follower_user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM follows WHERE follower_user_id = ?
        """,
        (follower_user_id,),
    )
    return _rows_to_dicts(await cursor.fetchall())

async def get_follows_by_followed(followed_user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM follows WHERE followed_user_id = ?
        """,
        (followed_user_id,),
    )
    return _rows_to_dicts(await cursor.fetchall())

async def delete_follow(follower_user_id: int, followed_user_id: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        DELETE FROM follows WHERE follower_user_id = ? AND followed_user_id = ?
        """,
        (follower_user_id, followed_user_id),
    )
    await db.commit()

# ══════════════════════════════════════════
# REFERRAL OPERATIONS
# ══════════════════════════════════════════

async def create_referral(
    referrer_id: int,
    referred_id: int,
) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        INSERT INTO referrals (referrer_id, referred_id)
        VALUES (?, ?)
        """,
        (referrer_id, referred_id),
    )
    await db.commit()

async def get_referrals_by_user(user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM referrals WHERE referrer_id = ? OR referred_id = ?
        """,
        (user_id, user_id),
    )
    return _rows_to_dicts(await cursor.fetchall())

# ══════════════════════════════════════════
# ACHIEVEMENT OPERATIONS
# ══════════════════════════════════════════

async def create_achievement(
    user_id: int,
    achievement_type: str,
) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        INSERT INTO achievements (user_id, achievement_type)
        VALUES (?, ?)
        """,
        (user_id, achievement_type),
    )
    await db.commit()

async def get_user_achievements(user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM achievements WHERE user_id = ? ORDER BY earned_at DESC
        """,
        (user_id,),
    )
    return _rows_to_dicts(await cursor.fetchall())

# ══════════════════════════════════════════
# DAILY CHECKIN OPERATIONS
# ══════════════════════════════════════════

async def create_daily_checkin(
    user_id: int,
    checkin_date: str,
) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        INSERT INTO daily_checkins (user_id, checkin_date)
        VALUES (?, ?)
        """,
        (user_id, checkin_date),
    )
    await db.commit()

async def get_user_daily_checkins(user_id: int) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM daily_checkins WHERE user_id = ? ORDER BY checkin_date DESC
        """,
        (user_id,),
    )
    return _rows_to_dicts(await cursor.fetchall())

async def get_user_last_daily_checkin(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        ""\"
        SELECT * FROM daily_checkins WHERE user_id = ? ORDER BY checkin_date DESC LIMIT 1
        """,
        (user_id,),
    )
    return _row_to_dict(await cursor.fetchone())

async def update_daily_streak(user_id: int, streak_count: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE daily_checkins SET streak_count = ?, updated_at = datetime('now') WHERE user_id = ? ORDER BY checkin_date DESC LIMIT 1
        """,
        (streak_count, user_id),
    )
    await db.commit()

async def update_daily_etoiles(user_id: int, etoiles_awarded: int) -> None:
    db = await get_db()
    await db.execute(
        ""\"
        UPDATE daily_checkins SET etoiles_awarded = ?, updated_at = datetime('now') WHERE user_id = ? ORDER BY checkin_date DESC LIMIT 1
        """,
        (etoiles_awarded, user_id),
    )
    await db.commit()
