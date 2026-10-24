# PAXG/USD Price Tracking Telegram Bot 🪙📈

An automated Telegram bot that tracks live **PAX Gold (PAXG/USD)** market prices from Delta Exchange and sends instant price alerts directly to your Telegram chat whenever the price drops by configured increments (e.g. $2.00).

---

## 🌟 Key Features

- **Live Market Tracking**: Real-time integration with Delta Exchange's public tickers API.
- **Support for Both Regional Markets**:
  - `PAXGUSD` on **Delta Exchange India** (`https://api.india.delta.exchange/v2/tickers`)
  - `PAXGUSDT` on **Delta Exchange Global** (`https://api.delta.exchange/v2/tickers`)
- **Step-based Downward Alerts**: Automatically calculates the next downward alert threshold (e.g., initial price minus $2) and continuously advances down if prices drop.
- **Resilient & Robust**:
  - Handles API retries, network hiccups, and rate limits gracefully.
  - Automatic fallback between Delta Exchange endpoints.
  - Clear terminal logging with timestamps.
- **Diagnostic Tooling**: Included `test_connection.py` to verify Telegram Bot tokens, chat IDs, and exchange endpoints before launching the continuous runner.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed
- A Telegram account

### 2. Clone the Repository
```bash
git clone https://github.com/PreMob/Telegram_paxgusd_bot.git
cd Telegram_paxgusd_bot
```

### 3. Create and Activate Virtual Environment (Optional but Recommended)
On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Telegram Bot & Environment Variables

1. Open Telegram and message [@BotFather](https://t.me/BotFather) to create a new bot:
   - Send `/newbot`
   - Follow instructions to choose a name and username.
   - Copy the API HTTP Token provided by BotFather.
2. Find your personal Telegram Chat ID:
   - Open your new bot in Telegram and click **Start** (`/start`).
   - Open this URL in your web browser (replace `<YOUR_TOKEN>` with your actual bot token):
     ```
     https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
     ```
   - Locate the `"chat":{"id": 123456789}` field. That number is your `TELEGRAM_CHAT_ID`.
3. Create a `.env` file in the project root (you can copy `.env.example`):
   ```bash
   cp .env.example .env
   ```
4. Fill in `.env` with your values:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_from_botfather
   TELEGRAM_CHAT_ID=your_chat_id
   DELTA_TICKER_URL=https://api.india.delta.exchange/v2/tickers
   DELTA_SYMBOL=PAXGUSD
   POLL_SECONDS=30
   ALERT_STEP=2.0
   ```

---

## 🔍 Diagnostics & Testing

Before running the continuous bot, test your configuration:
```bash
python test_connection.py
```
This tests:
1. Telegram Bot Token validity (`getMe`)
2. Telegram Chat messaging (`sendMessage`)
3. Delta Exchange API ticker fetching and PAXG price extraction

---

## 🏃 Running the Bot

Run the bot with:
```bash
python bot.py
```

### Expected Behavior:
1. The bot sends a test message to your Telegram chat:
   > 🤖 **PAXG Price Bot is Online!**
2. It fetches the current PAXG price from Delta Exchange and establishes the initial threshold:
   > 📊 **PAXGUSD Price Monitoring Active**  
   > 💰 Current Price: $4,003.10  
   > 🔔 First Downward Alert: $4,001.10  
   > ⏱ Poll Interval: 30s
3. Whenever the price reaches or crosses the downward threshold, an alert is sent:
   > 📉 **PAXGUSD PRICE ALERT**  
   > 💵 Current Price: $4,000.50  
   > 🔻 Downward Threshold: $4,001.10  
   > ⚠️ *Price alert only — not a trading instruction.*

---

## ⚙️ Configuration Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | API Token from BotFather | *Required* |
| `TELEGRAM_CHAT_ID` | Telegram user or group chat ID | *Required* |
| `DELTA_TICKER_URL` | Delta Exchange Tickers API URL | `https://api.india.delta.exchange/v2/tickers` |
| `DELTA_SYMBOL` | Market symbol to monitor (`PAXGUSD` or `PAXGUSDT`) | `PAXGUSD` |
| `POLL_SECONDS` | Seconds between market price checks | `30` |
| `ALERT_STEP` | Price drop amount (in USD) to trigger next alert | `2.0` |

---

## 🔒 Security Note
Never commit your `.env` file containing your Telegram Bot Token or personal chat ID to GitHub. The `.gitignore` file is configured to exclude all `.env` files automatically.

---

## 📄 License
MIT License.
