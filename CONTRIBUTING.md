# Contributing to FR Follow For Follow Bot

Thanks for your interest in contributing! Here's how you can help.

## Reporting Bugs

Open an [Issue](https://github.com/SoCloseSociety/FrFollowForFollowBot/issues) with:

- A clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

## Suggesting Features

Open a [Discussion](https://github.com/SoCloseSociety/FrFollowForFollowBot/discussions) in the **Ideas** category.

## Submitting Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to your branch (`git push origin feature/my-feature`)
5. Open a Pull Request

### Code Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use meaningful variable and function names
- Use async/await patterns consistently (Aiogram 3)

## Development Setup

```bash
git clone https://github.com/SoCloseSociety/FrFollowForFollowBot.git
cd FrFollowForFollowBot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
python bot.py
```

## Questions?

Open a [Discussion](https://github.com/SoCloseSociety/FrFollowForFollowBot/discussions) — we're happy to help!
