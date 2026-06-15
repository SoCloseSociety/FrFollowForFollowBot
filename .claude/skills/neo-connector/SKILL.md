---
name: neo-connector
description: Audit this repo's connectivity surface for NeoBot and regenerate NEO_CONNECTOR.md. Use when asked to wire this project to Neo, refresh the connector manifest, or check whether it exposes an API.
---

# Neo Connector audit -- frfollow

Goal: keep `NEO_CONNECTOR.md` an accurate, code-proven manifest of how (or whether)
NeoBot can talk to this repo. Never invent endpoints; prove everything from source.
Uncertain -> put it under `## Gaps`.

## Current verdict
NOT WIREABLE as an HTTP connector. This is a long-polling Telegram bot (aiogram 3.x).
The entry point `bot.py` calls `dp.start_polling(bot)` and exposes no inbound HTTP/
REST/WS/webhook server. Users interact only via Telegram chat commands. `aiohttp` in
requirements is aiogram's outbound transport, not a served port.

## How to re-audit
1. Inventory app source (exclude venvs): `find . -name '*.py' -not -path './.git/*' -not -path './.venv/*' -not -path './path/*' -not -path './__pycache__/*'`.
2. Look for any inbound server: `grep -rniE 'web\.Application|web\.run_app|set_webhook|SimpleRequestHandler|flask|fastapi|uvicorn|aiohttp\.web|@app\.(route|get|post)|listen\(' bot.py config.py handlers services middlewares database`.
3. Confirm transport mode: `grep -rn 'start_polling\|run_polling\|webhook' bot.py`. Polling -> NOT WIREABLE.
4. Capture env from `config.py` `Settings` (note which are required for startup -- see `bot.py`) and the command list from `set_bot_commands` in `bot.py`.
5. If a webhook/HTTP server is ever added -> document base_url, auth, and every endpoint (method, path, auth, input, output, errors, curl example), mirroring SuiteForge `editsforge/NEO_CONNECTOR.md`.
6. Do NOT modify source code during an audit. Only write `NEO_CONNECTOR.md`, this skill, the CLAUDE.md "Neo Connector (auto)" section, and the pre-commit hook.

## Files this audit owns
- `NEO_CONNECTOR.md` (the manifest)
- `CLAUDE.md` -> "## Neo Connector (auto)"
- `.claude/skills/neo-connector/SKILL.md` (this file)
- `.git/hooks/pre-commit` (staleness warning)
