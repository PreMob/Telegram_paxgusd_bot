# PAXG/USD Price Tracking Telegram Bot 🪙📈

An automated Telegram bot that tracks live **PAX Gold (PAXG/USD)** market prices from Delta Exchange and sends instant price alerts directly to your Telegram chat whenever the price moves **UP** or **DOWN** by configured step increments (e.g. $2.00).

---

## 🌟 Key Features

- **Live Market Tracking**: Real-time integration with Delta Exchange's public tickers API.
- **Bidirectional Price Alerts**:
  - 📈 **Upward Alerts**: Triggers when price rises above the upper threshold.
  - 📉 **Downward Alerts**: Triggers when price drops below the lower threshold.
  - **Dynamic Trailing Bracket**: Continuously repositions the step bracket around current market levels without spamming whipsaws.
- **Support for Both Regional Markets**:
  - `PAXGUSD` on **Delta Exchange India** (`https://api.india.delta.exchange/v2/tickers`)
  - `PAXGUSDT` on **Delta Exchange Global** (`https://api.delta.exchange/v2/tickers`)
- **Resilient & Robust**:
  - Handles API retries, network hiccups, and rate limits gracefully.
  - Telegram HTTP 429 backoff & rate-limit throttling (enforces ≥ 1.0s gap between messages).
  - Automatic fallback between Delta Exchange endpoints.
  - Timestamped terminal logs.
- **Diagnostic Tooling**: Included `test_connection.py` to verify Telegram Bot tokens, chat IDs, and exchange endpoints before launching the continuous runner.

---

## ⏱️ Polling Rate Limits: How low can `POLL_SECONDS` be?

| Setting | Recommendation | Details |
| :--- | :--- | :--- |
| `POLL_SECONDS=1` | **Fastest safe for REST** | Works for active real-time tracking during high-volatility sessions. |
| `POLL_SECONDS=2` - `5` | **Recommended 24/7** | Best balance between low latency, zero IP throttling, and stable continuous operation. |
| `< 1` (e.g. `0.5`) | **Not recommended over REST** | Delta Exchange tickers REST cache updates every ~500ms–1s anyway. Sub-second polling over HTTP increases latency overhead and risks temporary HTTP 429 / Cloudflare anti-DDoS IP blocks. |

> **Note on Telegram Rate Limits:** Telegram restricts bots to sending at most **1 message per second** to an individual private chat. The bot includes automatic message pacing and 429 retry backoff so rapid threshold breaks never crash your bot.

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

### 3. Create and Activate Virtual Environment (Optional)
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
   - Locate `"chat":{"id": 123456789}`. That number is your `TELEGRAM_CHAT_ID`.
3. Create a `.env` file in the project root:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_from_botfather
   TELEGRAM_CHAT_ID=your_chat_id
   DELTA_TICKER_URL=https://api.india.delta.exchange/v2/tickers
   DELTA_SYMBOL=PAXGUSD
   POLL_SECONDS=1
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
2. It fetches the current PAXG price from Delta Exchange and establishes both alert thresholds:
   > 📊 **PAXGUSD Price Monitoring Active**  
   > 💰 Current Price: $4,026.20  
   > 🔺 Upper Alert: $4,028.20 (+$2.00)  
   > 🔻 Lower Alert: $4,024.20 (-$2.00)  
   > ⏱ Poll Interval: 1s
3. Whenever the price crosses a threshold:
   - **Upward move**:
     > 📈 **PAXGUSD UPWARD ALERT**  
     > 💵 Current Price: $4,028.30  
     > 🔺 Crossed Level: $4,028.20  
     > 🎯 Next Targets: 🔺 $4,030.20 \| 🔻 $4,026.20
   - **Downward move**:
     > 📉 **PAXGUSD DOWNWARD ALERT**  
     > 💵 Current Price: $4,024.00  
     > 🔻 Crossed Level: $4,024.20  
     > 🎯 Next Targets: 🔺 $4,026.20 \| 🔻 $4,022.20

---

## ⚙️ Configuration Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | API Token from BotFather | *Required* |
| `TELEGRAM_CHAT_ID` | Telegram user or group chat ID | *Required* |
| `DELTA_TICKER_URL` | Delta Exchange Tickers API URL | `https://api.india.delta.exchange/v2/tickers` |
| `DELTA_SYMBOL` | Market symbol to monitor (`PAXGUSD` or `PAXGUSDT`) | `PAXGUSD` |
| `POLL_SECONDS` | Seconds between market price checks | `1` to `30` |
| `ALERT_STEP` | Price move amount (in USD) to trigger next alert | `2.0` |

---

## 🔒 Security Note
Never commit your `.env` file containing your Telegram Bot Token or personal chat ID to GitHub. The `.gitignore` file is configured to exclude all `.env` files automatically.

---

## 📄 License
MIT License.
