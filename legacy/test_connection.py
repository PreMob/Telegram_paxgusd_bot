import os
import sys

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
DEFAULT_TICKER_URL = os.getenv("DELTA_TICKER_URL", "https://api.india.delta.exchange/v2/tickers").strip()

print("=" * 55)
print(" PAXG Telegram Bot - Connectivity Diagnostic Tool ")
print("=" * 55)

# 1. Test Telegram Bot Token
print("\n[1/3] Testing Telegram Bot Token...")
if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN is empty in .env!")
else:
    try:
        res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        data = res.json()
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"✅ Telegram Token VALID!")
            print(f"   Bot Username: @{bot_info.get('username')}")
            print(f"   Bot Name: {bot_info.get('first_name')}")
            print(f"   Bot ID: {bot_info.get('id')}")
        else:
            print(f"❌ Telegram Token INVALID:")
            print(f"   Status Code: {res.status_code}")
            print(f"   Description: {data.get('description')}")
            print("   👉 Check your token from @BotFather in Telegram.")
    except Exception as e:
        print(f"❌ Error contacting Telegram API: {e}")

# 2. Test Telegram Chat ID & Send Message
print("\n[2/3] Testing Telegram Chat ID...")
if not CHAT_ID:
    print("❌ TELEGRAM_CHAT_ID is empty in .env!")
else:
    print(f"Configured Chat ID: {CHAT_ID}")
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": "🧪 <b>Telegram PAXG Bot Diagnostic Test</b>\nIf you see this, Telegram notifications are working!",
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        data = res.json()
        if data.get("ok"):
            print("✅ Successfully sent test message to your Telegram chat!")
        else:
            print(f"❌ Failed to send message to chat {CHAT_ID}:")
            print(f"   Description: {data.get('description')}")
            print("   👉 Ensure you clicked 'Start' in your bot before testing.")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

# 3. Test Delta Exchange API
print("\n[3/3] Testing Delta Exchange API endpoints...")
endpoints = [
    ("Delta India (PAXGUSD)", "https://api.india.delta.exchange/v2/tickers"),
    ("Delta Global (PAXGUSDT)", "https://api.delta.exchange/v2/tickers"),
]

for label, url in endpoints:
    try:
        res = requests.get(url, headers={"User-Agent": "TelegramBotTester/1.0"}, timeout=10)
        res.raise_for_status()
        data = res.json()
        items = data.get("result", [])
        paxg_matches = [x for x in items if "PAXG" in str(x.get("symbol", "")).upper()]
        if paxg_matches:
            match = paxg_matches[0]
            print(f"✅ {label}:")
            print(f"   Found Symbol: {match.get('symbol')}")
            print(f"   Close Price: ${match.get('close')}")
            print(f"   Spot Price:  ${match.get('spot_price')}")
            print(f"   Mark Price:  ${match.get('mark_price')}")
        else:
            print(f"⚠️ {label}: Connected, but no PAXG symbol found in {len(items)} tickers.")
    except Exception as e:
        print(f"❌ {label} failed: {e}")

print("\n" + "=" * 55)
print(" Diagnostic complete.")
print("=" * 55)
