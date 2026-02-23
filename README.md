<p align="center">
  <img src="assets/banner.svg" alt="FR Follow For Follow Bot" width="900">
</p>

<p align="center">
  <strong>Bot Telegram gamifié de follow-for-follow pour faire grandir ton Instagram — missions, niveaux, classement.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-575ECF?style=flat-square" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.13%2B-575ECF?style=flat-square&logo=python&logoColor=white" alt="Python 3.13+"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-575ECF?style=flat-square" alt="Platform">
  <a href="https://github.com/SoCloseSociety/FrFollowForFollowBot/stargazers"><img src="https://img.shields.io/github/stars/SoCloseSociety/FrFollowForFollowBot?style=flat-square&color=575ECF" alt="Stars"></a>
  <a href="https://github.com/SoCloseSociety/FrFollowForFollowBot/issues"><img src="https://img.shields.io/github/issues/SoCloseSociety/FrFollowForFollowBot?style=flat-square&color=575ECF" alt="Issues"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#key-features">Features</a> &bull;
  <a href="#how-it-works">How It Works</a> &bull;
  <a href="#faq">FAQ</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

---

## What is FR Follow For Follow Bot?

**FR Follow For Follow Bot** is a free, open-source Telegram bot that gamifies Instagram follow-for-follow exchanges for the French-speaking community. Users receive missions (5 accounts to follow), earn stars for completing them, level up, and climb a leaderboard — all managed automatically.

Unlike basic F4F bots, this one features a complete **gamification engine**: levels, achievements, streaks, referral bonuses, daily check-ins, and an optional auto-mode for premium users.

### Who is this for?

- **Instagram Creators** looking to grow organically in the French market
- **Social Media Managers** bootstrapping new accounts
- **Community Builders** running engagement groups on Telegram
- **Growth Hackers** exploring gamified acquisition strategies
- **Developers** learning async Python with Aiogram 3

### Key Features

- **Mission System** — Receive 5 accounts to follow per mission with verification
- **Gamification Engine** — Stars, levels (Débutant → Légende), achievements, streaks
- **Daily Check-ins** — 2 stars/day + 15-star bonus for 7-day streaks
- **Referral Program** — 10 stars per invited friend
- **Leaderboard** — Global ranking to foster competition
- **Auto Mode** — Premium feature: automated following for 24h (50 stars)
- **Admin Panel** — Full management via Telegram commands
- **Rate Limiting** — Smart delays with exponential backoff for Instagram safety
- **Session Persistence** — Avoids frequent Instagram re-logins
- **French UI** — Entirely in French for the target audience
- **Free & Open Source** — MIT license

---

## Quick Start

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.13+ ([Download](https://www.python.org/downloads/)) |
| **Telegram Bot Token** | Create via [@BotFather](https://t.me/BotFather) |
| **Instagram Account** | A dedicated account for the bot |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SoCloseSociety/FrFollowForFollowBot.git
cd FrFollowForFollowBot

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your credentials

# 5. Run
python bot.py
```

---

## How It Works

```
User joins Telegram Group
         │
         ▼
┌─────────────────────────────┐
│     FrFollowForFollowBot    │
│                             │
│  1. User registers IG link  │
│  2. Receives mission (5 IG) │
│  3. Follows the 5 accounts  │
│  4. Bot verifies via API    │
│  5. Stars awarded (3/follow)│
│  6. Level up + leaderboard  │
└─────────────────────────────┘
         │
         ▼
   SQLite Database
   (users, missions, follows)
```

### Gamification System

| Action | Stars Earned |
|--------|-------------|
| Follow completed | 3 stars |
| Received a follow | 1 star |
| Referral | 10 stars |
| Daily check-in | 2 stars |
| 7-day streak bonus | 15 stars |
| Welcome bonus | 5 stars |

| Level | Name |
|-------|------|
| 1 | Débutant |
| 2 | Explorateur |
| 3 | Influenceur |
| 4 | Star |
| 5 | Légende |

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `INSTAGRAM_USERNAME` | Bot's Instagram username |
| `INSTAGRAM_PASSWORD` | Bot's Instagram password |
| `ADMIN_TELEGRAM_IDS` | Comma-separated admin Telegram IDs |

---

## Project Structure

```
FrFollowForFollowBot/
├── bot.py                  # Main entry point
├── config.py               # Settings management (Pydantic)
├── requirements.txt        # Dependencies
├── .env.example            # Configuration template
├── database/
│   ├── db.py               # DB connection & init
│   ├── models.py           # SQL table definitions
│   └── queries.py          # Query functions
├── handlers/
│   ├── start.py            # Registration & /start
│   ├── mission.py          # Mission generation
│   ├── verify.py           # Follow verification
│   ├── profile.py          # User profile
│   ├── leaderboard.py      # Rankings
│   ├── referral.py         # Referral links
│   ├── auto_mode.py        # Auto-mode feature
│   ├── settings.py         # User preferences
│   ├── help.py             # Help command
│   └── admin.py            # Admin panel
├── keyboards/
│   ├── inline.py           # Inline buttons
│   └── callbacks.py        # Callback data
├── services/
│   ├── instagram.py        # Instagram API + rate limiter
│   ├── mission_engine.py   # Mission algorithm
│   ├── gamification.py     # Points & achievements
│   └── scheduler.py        # Background jobs
├── middlewares/
│   └── auth.py             # Authentication
├── utils/
│   ├── helpers.py          # Utility functions
│   └── texts.py            # French UI strings
└── scripts/
    └── seed_pool.py        # DB seeding
```

---

## Troubleshooting

### Bot doesn't start

1. Check your `.env` — make sure the Telegram token is valid
2. Verify Python 3.13+ with `python --version`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

### Instagram login fails

1. Disable 2FA on the bot's Instagram account
2. Log in manually first to clear security challenges
3. Wait a few hours if rate-limited

### Verification fails

1. Instagram may have restricted the bot — increase delays in config
2. Target account may be private
3. Check logs for specific error messages

---

## FAQ

**Q: Is this free?**
A: Yes. 100% free and open source under MIT license.

**Q: Is this safe for my Instagram?**
A: Use reasonable limits. The bot includes rate limiting and human-like delays, but aggressive usage can trigger Instagram restrictions.

**Q: Can I change the language?**
A: The UI strings are in `utils/texts.py` — you can translate them to any language.

**Q: How many users can it handle?**
A: SQLite with WAL mode handles hundreds of concurrent users easily. For thousands, consider migrating to PostgreSQL.

---

## Alternatives Comparison

| Feature | FrFollowForFollowBot | Manual F4F | Paid Growth |
|---------|---------------------|------------|-------------|
| Price | **Free** | Free | $20-100/mo |
| Gamification | Yes (levels, stars) | No | No |
| Automated | Yes | No | Yes |
| Fair exchange | Yes (mission system) | Trust-based | N/A |
| Open source | Yes | N/A | No |

---

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) before submitting a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Disclaimer

This tool is provided for **educational purposes only**. Automated interactions may violate Instagram's Terms of Service. Use responsibly and at your own risk. The authors are not responsible for any account restrictions.

---

<p align="center">
  <strong>If this project helps you, please give it a star!</strong><br>
  <a href="https://github.com/SoCloseSociety/FrFollowForFollowBot">
    <img src="https://img.shields.io/github/stars/SoCloseSociety/FrFollowForFollowBot?style=for-the-badge&logo=github&color=575ECF" alt="Star this repo">
  </a>
</p>

<br>

<p align="center">
  <sub>Built with purpose by <a href="https://soclose.co"><strong>SoClose</strong></a> &mdash; Digital Innovation Through Automation & AI</sub><br>
  <sub>
    <a href="https://soclose.co">Website</a> &bull;
    <a href="https://linkedin.com/company/soclose-agency">LinkedIn</a> &bull;
    <a href="https://twitter.com/SoCloseAgency">Twitter</a> &bull;
    <a href="mailto:contact@soclose.co">Contact</a>
  </sub>
</p>
