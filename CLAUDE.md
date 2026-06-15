# CLAUDE.md -- FrFollowForFollowBot

## 1. Project Identity

**Name:** FrFollowForFollowBot -- French Instagram F4F Gamified Bot
**Role:** Modern async Telegram bot for Instagram follow-for-follow with gamification (levels, achievements, streaks, daily check-ins, premium auto-mode). Fully in French.
**Author:** SoClose Society (https://soclose.co)
**License:** MIT

### Stack

- **Language:** Python 3.13+
- **Bot Framework:** aiogram 3.x (async)
- **Instagram:** instagrapi (API client)
- **Database:** aiosqlite (async SQLite)
- **Config:** pydantic-settings + python-dotenv
- **Scheduling:** APScheduler
- **HTTP:** aiohttp

### Architecture Overview

```
bot.py (entry point, 127 LOC)
├── config.py              Pydantic Settings management
├── database/
│   ├── db.py              Async SQLite connection
│   ├── models.py          Schema definitions
│   └── queries.py         Query layer (638 LOC)
├── handlers/              Aiogram routers
│   ├── start.py           Registration/welcome
│   ├── mission.py         Mission assignment
│   ├── verify.py          Follow verification (214 LOC)
│   ├── profile.py         User profile display
│   ├── leaderboard.py     Ranking system
│   ├── referral.py        Referral system
│   ├── admin.py           Admin operations
│   ├── settings.py        User preferences
│   ├── auto_mode.py       Auto-mode handler
│   └── help.py            Help docs
├── services/
│   ├── instagram.py       Instagram API + rate limiting (326 LOC)
│   ├── gamification.py    XP/levels/achievements (181 LOC)
│   ├── mission_engine.py  Mission generation
│   └── scheduler.py       APScheduler integration
├── keyboards/             Inline keyboard builders
├── middlewares/auth.py     Auth middleware
├── utils/texts.py          French UI strings (318 LOC)
├── scripts/seed_pool.py    DB initialization
└── tests/test_integration.py  Integration tests (689 LOC)
```

~4,159 total lines of Python.

### Critical Files -- Do Not Touch Without a Plan

- `services/instagram.py` -- Rate limiter with exponential backoff
- `services/gamification.py` -- Points/levels system (Etoiles currency)
- `database/queries.py` -- Core query layer (638 LOC)
- `utils/texts.py` -- All French UI strings (318 LOC)

## 2-5. Standard Workflow

- Enter plan mode for non-trivial tasks
- Test with single user flow before deploying
- Run integration tests: `pytest tests/`
- All UI text is in French -- maintain consistency
- Track tasks in `tasks/todo.md`, lessons in `tasks/lessons.md`

## 6. Project-Specific Rules

### Dev Commands
```bash
pip install -r requirements.txt
cp .env.example .env  # Fill in credentials
python scripts/seed_pool.py  # Initialize DB
python bot.py

# Run tests
pytest tests/test_integration.py
```

### Environment Variables
- TELEGRAM_BOT_TOKEN -- Bot token
- INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD -- Bot Instagram account
- INSTAGRAM_PROXY -- Optional proxy for Instagram
- DATABASE_PATH -- SQLite path (default: data/bot.db)
- ETOILES_PER_FOLLOW_GIVEN=3, ETOILES_PER_FOLLOW_RECEIVED=1
- ETOILES_PER_REFERRAL=10, ETOILES_WELCOME_BONUS=5
- AUTO_MODE_COST=50, AUTO_MODE_DURATION_HOURS=24
- MISSION_SIZE=5
- INSTAGRAM_REQUEST_DELAY_MIN=5, INSTAGRAM_REQUEST_DELAY_MAX=15
- MAX_VERIFICATIONS_PER_HOUR=20
- ADMIN_TELEGRAM_IDS -- Comma-separated admin IDs

### Gamification Levels
- Debutant -> Explorateur -> Influenceur -> Star -> Legende (based on Etoiles)

### Known Fragile Areas
- instagrapi -- Instagram API changes can break follow verification
- Rate limiting -- Exponential backoff params are tuned, don't change blindly
- French text -- All UI in French, maintain translation consistency
- Async SQLite -- aiosqlite can have locking issues under high concurrency

## 7. Core Principles

- Simplicity First, No Laziness, Minimal Impact
- Never use em dashes (use -- instead)
- Ollama-first for any local LLM calls (RTX 4070 available)
- All UI text must remain in French

## Neo Connector (auto)

- Slug: `frfollow`
- Verdict: NOT WIREABLE -- long-polling Telegram bot (aiogram 3.x), no inbound HTTP server. The only entry is `dp.start_polling(bot)` in `bot.py`; users interact via Telegram chat only.
- Manifest: `NEO_CONNECTOR.md` (proven from `bot.py` + `config.py`; regenerate via the Neo Connector audit).
- For Neo: there is no port/endpoint to call. Do not invent endpoints. The bot's `/start`, `/mission`, `/verifier`, etc. are Telegram commands, not HTTP. If wiring is ever needed, an aiogram webhook + RPC endpoint or a separate HTTP service over `database/queries.py` would have to be built (out of scope; would modify the project).
- Startup env: `TELEGRAM_BOT_TOKEN` is required; Instagram creds optional (verification disabled without them). Full env list in `NEO_CONNECTOR.md`.
- When `bot.py` or `config.py` change, re-run the audit and regenerate `NEO_CONNECTOR.md`. The pre-commit hook warns if they changed without touching `NEO_CONNECTOR.md`.
