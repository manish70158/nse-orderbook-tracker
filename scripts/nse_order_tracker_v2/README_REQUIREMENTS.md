# Requirements Files

This project has two requirements files:

## 1. `requirements.txt` (Base Dependencies)

**Purpose:** Core functionality for NSE order book tracking

**Includes:**
- Flask (dashboard)
- Pandas (data processing)
- Requests (API calls)
- PyPDF2, pdfplumber (PDF parsing)
- Playwright (browser automation - unused in V2 but kept for compatibility)

**Used by:**
- `orchestrator.py` (main scraper)
- `app.py` (dashboard server)
- `telegram_notifier.py` (basic notifications)
- GitHub Actions workflow (daily automation)

**Install:**
```bash
pip install -r requirements.txt
```

---

## 2. `requirements-bot.txt` (Bot Server Additional Dependencies)

**Purpose:** Interactive Telegram bot for real-time data fetching

**Includes:**
- `python-telegram-bot==20.7` (interactive bot library)

**Used by:**
- `telegram_bot_server.py` (interactive bot server only)

**Install:**
```bash
# After installing base requirements
pip install -r requirements-bot.txt
```

---

## Installation Guide

### For Daily Automation Only (Recommended)

If you only want daily automated reports via GitHub Actions:

```bash
pip install -r requirements.txt
python orchestrator.py --days 3
```

**You do NOT need** `requirements-bot.txt` for this.

---

### For Interactive Bot Server

If you want to run the interactive bot that responds to commands:

```bash
# Install both
pip install -r requirements.txt
pip install -r requirements-bot.txt

# Start bot server
python telegram_bot_server.py
```

---

## Why Two Files?

**Reason:** The `python-telegram-bot` library is quite large and has many dependencies. It's only needed for the interactive bot server (`telegram_bot_server.py`).

**Benefits:**
- ✅ Faster installation for basic usage
- ✅ Smaller docker images
- ✅ GitHub Actions runs faster (doesn't install unused dependencies)
- ✅ Fewer potential conflicts

**GitHub Actions:** Uses only `requirements.txt` since it just runs `orchestrator.py` for daily automation.

---

## Dependency Tree

```
requirements.txt (Core - Always Install)
├── Flask (dashboard)
├── Pandas (data processing)
├── Requests (HTTP)
├── PyPDF2 (PDF parsing)
├── pdfplumber (PDF parsing)
├── openpyxl (Excel export)
├── beautifulsoup4 (HTML parsing)
├── playwright (legacy, unused)
└── python-dotenv (env vars)

requirements-bot.txt (Optional - Only for Interactive Bot)
└── python-telegram-bot (interactive bot framework)
    ├── httpx (async HTTP)
    ├── certifi (SSL)
    └── [many other dependencies]
```

---

## Quick Reference

| Use Case | Install |
|----------|---------|
| Daily automation (GitHub Actions) | `requirements.txt` |
| Dashboard only | `requirements.txt` |
| Basic Telegram notifications | `requirements.txt` |
| **Interactive bot server** | `requirements.txt` + `requirements-bot.txt` |

---

## Troubleshooting

### "No module named 'telegram'"

**Problem:** You're trying to run `telegram_bot_server.py` without bot dependencies

**Solution:**
```bash
pip install -r requirements-bot.txt
```

### GitHub Actions failing with telegram error

**Problem:** Workflow shouldn't need telegram bot library

**Solution:** Workflow uses only `requirements.txt`, not `requirements-bot.txt`. This is correct.

### Installation takes too long

**Problem:** Installing all dependencies including bot library

**Solution:** Only install what you need:
- For automation: `requirements.txt` only
- For interactive bot: both files

---

## Version Information

- **requirements.txt**: Updated regularly with core dependencies
- **requirements-bot.txt**: Stable, rarely updated
- **Python version**: 3.11+ recommended

---

Last updated: 2026-06-08
