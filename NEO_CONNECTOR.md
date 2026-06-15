# NEO_CONNECTOR -- frfollow
- service: frfollow
- base_url_prod: none (no HTTP server)
- auth: none (no inbound network surface; users interact only via Telegram)
- env_required: [TELEGRAM_BOT_TOKEN]  # bot will not start without it (bot.py)
- generated_at:

> Machine-readable connection manifest for NeoBot. Everything below is proven from
> code. Do NOT edit by hand -- regenerate via the Neo Connector audit.
>
> VERDICT: NOT WIREABLE as an HTTP connector. This is a long-polling Telegram bot
> (aiogram 3.x). It exposes NO inbound HTTP/REST/WS/webhook endpoint -- it pulls
> updates from Telegram via `dp.start_polling(bot)`. There is no port for Neo to
> call. Interaction happens only through Telegram chat commands.

## What this is (proven from source)
- Entry point: `bot.py` -> `main()` -> `await dp.start_polling(bot)` (line 123).
  No `web.Application`, no `web.run_app`, no webhook registration anywhere.
- Framework: aiogram 3.x `Dispatcher` + `Bot`, routers in `handlers/`, auth via
  `middlewares/auth.py`, persistence `aiosqlite` (`database/`), background jobs via
  APScheduler (`services/scheduler.py`), Instagram via instagrapi (`services/instagram.py`).
- `aiohttp` (requirements) is aiogram's OUTBOUND transport to the Telegram Bot API;
  it does not start a listening server here.
- Startup hard-requires `TELEGRAM_BOT_TOKEN` (bot.py exits if unset/placeholder).

## User-facing commands (NOT an API; Telegram only -- from `set_bot_commands`)
`/start` (inscription/accueil), `/mission` (nouvelle mission), `/verifier`
(vérifier les follows), `/profil` (profil + stats), `/classement` (leaderboard),
`/parrainage` (lien de parrainage), `/auto` (mode automatique), `/parametres`
(paramètres), `/aide` (aide). These are reachable only by a Telegram user, not by Neo over HTTP.

## Run (the only "interface")
```bash
pip install -r requirements.txt
cp .env.example .env           # fill credentials
python scripts/seed_pool.py    # init DB
python bot.py                  # starts long-polling
```

## Config / env (proven from `config.py` Settings)
- `TELEGRAM_BOT_TOKEN` (required to start)
- `INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`, `INSTAGRAM_PROXY` (optional; verification disabled if unset)
- `DATABASE_PATH` (default `data/bot.db`)
- Gamification/rate-limit tunables: `ETOILES_PER_FOLLOW_GIVEN` (3), `ETOILES_PER_FOLLOW_RECEIVED` (1),
  `ETOILES_PER_REFERRAL` (10), `ETOILES_REFERRAL_FIRST_MISSION` (5), `ETOILES_DAILY_LOGIN` (2),
  `ETOILES_STREAK_7_DAYS` (15), `ETOILES_WELCOME_BONUS` (5), `AUTO_MODE_COST` (50),
  `AUTO_MODE_DURATION_HOURS` (24), `MISSION_SIZE` (5), `INSTAGRAM_REQUEST_DELAY_MIN` (5),
  `INSTAGRAM_REQUEST_DELAY_MAX` (15), `MAX_VERIFICATIONS_PER_HOUR` (20)
- `ADMIN_TELEGRAM_IDS` (comma-separated; parsed by `Settings.admin_ids`)

## Endpoints
None. No HTTP server exists in this repo.

## Gaps
- No inbound HTTP/REST/GraphQL/WebSocket/webhook server (verified: the only polling/
  server hit in source is `dp.start_polling` in bot.py; no flask/fastapi/uvicorn/
  web.Application/run_app/webhook anywhere).
- To make this Neo-callable you would need either (a) an aiogram webhook + a thin
  command/RPC endpoint, or (b) a separate HTTP service over its SQLite DB / query
  layer. Neither exists today; building one would modify the project -- out of scope.
- Bot identity (which Telegram bot, admin IDs) lives in `.env`, which is not audited
  here for secret values.
