TABLES_SQL = [
    # ── Users ──
    """
    CREATE TABLE IF NOT EXISTS users (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id             INTEGER UNIQUE NOT NULL,
        telegram_username       TEXT,
        instagram_username      TEXT UNIQUE,
        instagram_user_pk       TEXT,
        etoiles                 INTEGER NOT NULL DEFAULT 0,
        level                   TEXT NOT NULL DEFAULT 'Debutant',
        current_streak          INTEGER NOT NULL DEFAULT 0,
        longest_streak          INTEGER NOT NULL DEFAULT 0,
        total_follows_given     INTEGER NOT NULL DEFAULT 0,
        total_follows_received  INTEGER NOT NULL DEFAULT 0,
        referrer_id             INTEGER REFERENCES users(id),
        referral_code           TEXT UNIQUE NOT NULL,
        auto_mode_until         TEXT,
        is_banned               INTEGER NOT NULL DEFAULT 0,
        is_registered           INTEGER NOT NULL DEFAULT 0,
        notifications_enabled   INTEGER NOT NULL DEFAULT 1,
        last_daily_checkin      TEXT,
        last_verification_at    TEXT,
        created_at              TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)",
    "CREATE INDEX IF NOT EXISTS idx_users_instagram_username ON users(instagram_username)",
    "CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code)",
    "CREATE INDEX IF NOT EXISTS idx_users_etoiles ON users(etoiles DESC)",

    # ── Missions ──
    """
    CREATE TABLE IF NOT EXISTS missions (
        id                          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id                     INTEGER NOT NULL REFERENCES users(id),
        batch_id                    TEXT NOT NULL,
        target_instagram_username   TEXT NOT NULL,
        target_user_id              INTEGER REFERENCES users(id),
        status                      TEXT NOT NULL DEFAULT 'pending',
        created_at                  TEXT NOT NULL DEFAULT (datetime('now')),
        verified_at                 TEXT,
        expires_at                  TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_missions_user_id ON missions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_missions_batch_id ON missions(batch_id)",
    "CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status)",

    # ── Follows ──
    """
    CREATE TABLE IF NOT EXISTS follows (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        follower_user_id    INTEGER NOT NULL REFERENCES users(id),
        followed_user_id    INTEGER NOT NULL REFERENCES users(id),
        mission_id          INTEGER REFERENCES missions(id),
        verified            INTEGER NOT NULL DEFAULT 0,
        created_at          TEXT NOT NULL DEFAULT (datetime('now')),
        verified_at         TEXT,
        UNIQUE(follower_user_id, followed_user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_user_id)",
    "CREATE INDEX IF NOT EXISTS idx_follows_followed ON follows(followed_user_id)",

    # ── Referrals ──
    """
    CREATE TABLE IF NOT EXISTS referrals (
        id                      INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id             INTEGER NOT NULL REFERENCES users(id),
        referred_id             INTEGER NOT NULL REFERENCES users(id),
        signup_bonus_claimed    INTEGER NOT NULL DEFAULT 0,
        mission_bonus_claimed   INTEGER NOT NULL DEFAULT 0,
        created_at              TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(referrer_id, referred_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id)",

    # ── Achievements ──
    """
    CREATE TABLE IF NOT EXISTS achievements (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id             INTEGER NOT NULL REFERENCES users(id),
        achievement_type    TEXT NOT NULL,
        earned_at           TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, achievement_type)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_achievements_user ON achievements(user_id)",

    # ── Daily Checkins ──
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id             INTEGER NOT NULL REFERENCES users(id),
        checkin_date        TEXT NOT NULL,
        streak_count        INTEGER NOT NULL DEFAULT 1,
        etoiles_awarded     INTEGER NOT NULL DEFAULT 0,
        created_at          TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, checkin_date)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_checkins_user_date ON daily_checkins(user_id, checkin_date)",
]
