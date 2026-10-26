# Telegram Trading Community Platform 📈🤖

A modular, extensible platform designed to power trading communities with market tracking, signal processing, community engagement, and analytics.

> **Note on Safety:** Personal trading and order execution modules are strictly decoupled and **disabled by default** (`ENABLE_TRADE_EXECUTION=false`). No exchange trading credentials or order-placement capabilities are active at this stage.

---

## 🏗️ Architecture & Directory Structure

The project is structured into clear domain boundaries:

```text
trading-community-platform/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Application foundation entry point
│   ├── config.py                # Environment-based configuration & validation
│   ├── logging_config.py        # Reusable structured logging setup
│   │
│   ├── integrations/            # External integrations (Telegram, Delta Exchange)
│   │   └── __init__.py
│   │
│   ├── signals/                 # Signal ingestion, parsing & price alert rules
│   │   └── __init__.py
│   │
│   ├── engagement/              # Scheduled community posts, polls & recaps
│   │   └── __init__.py
│   │
│   ├── analytics/               # Signal performance, target hit rate & P&L tracking
│   │   └── __init__.py
│   │
│   ├── database/                # Database models, persistence & migrations
│   │   └── __init__.py
│   │
│   └── trading/                 # Isolated personal trading execution (disabled)
│       └── __init__.py
│
├── tests/                       # Automated test suite
│   ├── __init__.py
│   ├── test_config.py
│   └── test_smoke.py
│
├── legacy/                      # Preserved standalone scripts (e.g. PAXG alert prototype)
│   ├── bot.py
│   └── test_connection.py
│
├── .env.example                 # Configuration template with placeholder values
├── .gitignore                   # Git exclusion rules for secrets, DBs, sessions & venv
├── requirements.txt             # Pinned foundation dependencies
└── README.md                    # Project documentation
```

---

## 🐍 Requirements & Python Version

- **Python Version**: **Python 3.10+** (Tested and verified on Python 3.12.7)
- **Supported Operating Systems**: Windows, macOS, Linux

---

## 🚀 Environment Setup

### 1. Create the Local Virtual Environment

```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment

- **On Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **On Linux / macOS (Bash/Zsh):**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` to configure your local settings:

```powershell
Copy-Item .env.example .env
```

Edit `.env` to provide your configuration:

```dotenv
# Application Environment & Logging
APP_ENV=development
LOG_LEVEL=INFO
TIMEZONE=Asia/Kolkata

# Telegram Bot Credentials (from @BotFather)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
TELEGRAM_CHAT_ID=

# Delta Exchange Market Data API
DELTA_BASE_URL=https://api.india.delta.exchange/v2
DELTA_SYMBOL=PAXGUSD

# Database Persistence
DATABASE_URL=sqlite:///./tradebot.db

# Feature Toggles (Safely disabled by default)
ENABLE_COMMUNITY_BOT=false
ENABLE_PRICE_ALERTS=false
ENABLE_TRADE_EXECUTION=false
```

---

## 🏃 Running the Application

Run the application foundation using Python module execution:

```powershell
python -m app.main
```

### Expected Output:
```text
[2026-10-26 22:45:00] [INFO] [app]: ============================================================
[2026-10-26 22:45:00] [INFO] [app]: Trading Community Platform foundation initialized
[2026-10-26 22:45:00] [INFO] [app]: Environment: development | Log Level: INFO
[2026-10-26 22:45:00] [INFO] [app]: Market Symbol: PAXGUSD | Timezone: Asia/Kolkata
[2026-10-26 22:45:00] [INFO] [app]: Feature Toggles -> Community Bot: False | Price Alerts: False | Trade Execution: False
[2026-10-26 22:45:00] [INFO] [app]: Foundation ready. No background polling or orders active.
[2026-10-26 22:45:00] [INFO] [app]: ============================================================
```

---

## 🧪 Running Automated Tests

Run the test suite with `pytest`:

```powershell
pytest
```

To run with verbose output:
```powershell
pytest -v
```

---

## 📦 Preserved Legacy Scripts

The earlier standalone PAXG alert prototype and connectivity diagnostics have been preserved under [`legacy/`](file:///c:/Users/pbpan/OneDrive/Desktop/New%20folder/Telegram_bot/legacy):
- [`legacy/bot.py`](file:///c:/Users/pbpan/OneDrive/Desktop/New%20folder/Telegram_bot/legacy/bot.py): Standalone bidirectional PAXG/USD alert prototype.
- [`legacy/test_connection.py`](file:///c:/Users/pbpan/OneDrive/Desktop/New%20folder/Telegram_bot/legacy/test_connection.py): Diagnostic connectivity checker for BotFather credentials and Delta Exchange.

---

## 🔒 Security & Secrets Policy

1. `.env` and `.venv/` are excluded by `.gitignore` and **must never be committed**.
2. Database files (`*.db`), Telegram session files (`*.session`), and cache folders (`.pytest_cache/`, `__pycache__/`) are excluded.
3. Live order placement and trade execution are disabled by default.
