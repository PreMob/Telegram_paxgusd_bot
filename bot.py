import os
import sys
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables from .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Delta Exchange API endpoints
# Note: https://api.india.delta.exchange/v2/tickers serves PAXGUSD
#       https://api.delta.exchange/v2/tickers serves PAXGUSDT
DEFAULT_TICKER_URL = "https://api.india.delta.exchange/v2/tickers"
FALLBACK_TICKER_URL = "https://api.delta.exchange/v2/tickers"

configured_ticker_url = os.getenv("DELTA_TICKER_URL", "").strip()
# Auto-correct obsolete or empty ticker URL if publicapi.deltaexchange.io was provided
if not configured_ticker_url or "publicapi.deltaexchange.io" in configured_ticker_url:
    TICKER_URL = DEFAULT_TICKER_URL
else:
    TICKER_URL = configured_ticker_url

SYMBOL = os.getenv("DELTA_SYMBOL", "").strip().upper()

try:
    POLL_SECONDS = float(os.getenv("POLL_SECONDS", "30"))
except ValueError:
    POLL_SECONDS = 30.0

try:
    STEP = float(os.getenv("ALERT_STEP", "2.0"))
except ValueError:
    STEP = 2.0

TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
_last_msg_time = 0.0


def log(msg: str):
    """Print log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def send_message(text: str) -> bool:
    """Send a message to the configured Telegram chat with rate-limit protection."""
    global _last_msg_time

    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    # Enforce at least 1.0s gap between messages to comply with Telegram rate limits
    now = time.time()
    elapsed = now - _last_msg_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    url = f"{TELEGRAM_BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, timeout=15)

            # Handle Telegram rate limits (HTTP 429)
            if response.status_code == 429:
                retry_after = 2
                try:
                    retry_after = int(response.json().get("parameters", {}).get("retry_after", 2))
                except Exception:
                    pass
                log(f"Telegram rate limited (429). Retrying after {retry_after}s...")
                time.sleep(retry_after)
                continue

            if response.status_code == 401:
                raise RuntimeError(
                    "Telegram Bot API returned 401 Unauthorized. "
                    "Please check TELEGRAM_BOT_TOKEN in your .env file."
                )

            response.raise_for_status()
            result = response.json()
            if not result.get("ok"):
                raise RuntimeError(result.get("description", "Unknown Telegram error"))

            _last_msg_time = time.time()
            return True

        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(1)

    return False


def get_tickers(ticker_url: str = TICKER_URL) -> dict:
    """Fetch tickers from Delta Exchange and index by symbol."""
    headers = {
        "User-Agent": "TelegramPAXGUSDTracker/1.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(ticker_url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        # If default India URL fails and fallback wasn't already used, try Global
        if ticker_url == DEFAULT_TICKER_URL:
            log(f"India ticker endpoint failed ({exc}), trying fallback: {FALLBACK_TICKER_URL}")
            response = requests.get(FALLBACK_TICKER_URL, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        else:
            raise

    # Response is typically {"success": true, "result": [...]}
    if isinstance(data, dict) and "result" in data:
        items = data["result"]
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        return data
    else:
        raise ValueError(f"Unexpected ticker API response format: {type(data)}")

    # Index list of ticker objects by symbol for O(1) lookup
    tickers_dict = {}
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and "symbol" in item:
                tickers_dict[item["symbol"]] = item
    elif isinstance(items, dict):
        tickers_dict = items

    return tickers_dict


def find_paxg_symbols(tickers: dict) -> list:
    """Find all symbols related to PAXG in ticker results."""
    return [key for key in tickers.keys() if "PAXG" in key.upper()]


def get_price(tickers: dict, symbol: str) -> float:
    """Extract the current price from ticker data."""
    ticker = tickers.get(symbol)
    if not isinstance(ticker, dict):
        raise KeyError(f"Symbol {symbol!r} not found in Delta ticker response")

    # Try close price, then spot price, mark price, or last price
    for field in ("close", "spot_price", "mark_price", "last"):
        val = ticker.get(field)
        if val is not None:
            try:
                num = float(val)
                if num > 0:
                    return num
            except (ValueError, TypeError):
                continue

    raise ValueError(f"No valid price available for {symbol}")


def main():
    log("==========================================")
    log(" Starting PAXG Price Tracker Telegram Bot ")
    log("==========================================")

    if not BOT_TOKEN:
        log("ERROR: TELEGRAM_BOT_TOKEN is not configured in .env")
        sys.exit(1)
    if not CHAT_ID:
        log("ERROR: TELEGRAM_CHAT_ID is not configured in .env")
        sys.exit(1)

    log(f"Configured Ticker URL: {TICKER_URL}")
    log(f"Alert Step: ${STEP:.2f} | Poll Interval: {POLL_SECONDS}s")

    # Step 1: Verify Telegram messaging
    try:
        log("Testing Telegram connection...")
        send_message(
            "<b>🤖 PAXG Price Bot is Online!</b>\n\n"
            "✅ Private-chat test successful.\n"
            "📡 Connecting to Delta Exchange..."
        )
        log("Telegram test message sent successfully.")
    except Exception as exc:
        log(f"Failed to send Telegram message: {exc}")
        log("Please verify your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env.")
        sys.exit(1)

    # Step 2: Connect to Delta Exchange and detect PAXG symbol
    try:
        log("Fetching tickers from Delta Exchange...")
        tickers = get_tickers(TICKER_URL)
        candidates = find_paxg_symbols(tickers)
        log(f"PAXG-related symbols found: {candidates}")
    except Exception as exc:
        log(f"Failed to fetch Delta tickers: {exc}")
        send_message(f"❌ <b>Delta Exchange Error</b>\nFailed to connect: {exc}")
        sys.exit(1)

    # Resolve symbol
    symbol = SYMBOL
    if not symbol:
        exact_matches = [k for k in candidates if k.upper() in ("PAXGUSD", "PAXGUSDT")]
        if len(exact_matches) == 1:
            symbol = exact_matches[0]
        elif "PAXGUSD" in candidates:
            symbol = "PAXGUSD"
        elif "PAXGUSDT" in candidates:
            symbol = "PAXGUSDT"
        else:
            msg = (
                "⚠️ <b>Market Selection Warning</b>\n"
                f"Could not automatically select PAXG market.\n"
                f"Available matching symbols: <code>{candidates or 'None'}</code>\n"
                "Please specify DELTA_SYMBOL in your .env file."
            )
            send_message(msg)
            log("Set DELTA_SYMBOL in .env to the exact supported symbol, then restart.")
            sys.exit(1)

    # Step 3: Establish initial price and both UP and DOWN thresholds
    try:
        price = get_price(tickers, symbol)
        upper_threshold = price + STEP
        lower_threshold = price - STEP
    except Exception as exc:
        log(f"Failed to read price for {symbol}: {exc}")
        send_message(f"❌ <b>Error</b>: Could not get initial price for {symbol}: {exc}")
        sys.exit(1)

    log(f"Monitoring {symbol} starting at ${price:,.2f}")
    log(f"Initial Thresholds: 🔻 Lower: ${lower_threshold:,.2f} | 🔺 Upper: ${upper_threshold:,.2f}")

    start_notice = (
        f"📊 <b>{symbol} Price Monitoring Active</b>\n\n"
        f"💰 <b>Current Price:</b> ${price:,.2f}\n"
        f"🔺 <b>Upper Alert:</b> ${upper_threshold:,.2f} (+${STEP:,.2f})\n"
        f"🔻 <b>Lower Alert:</b> ${lower_threshold:,.2f} (-${STEP:,.2f})\n"
        f"📏 <b>Step Size:</b> ${STEP:,.2f}\n"
        f"⏱ <b>Poll Interval:</b> {POLL_SECONDS}s\n\n"
        f"<i>Bot will alert on both upward and downward price moves.</i>"
    )
    send_message(start_notice)

    # Step 4: Monitoring Loop
    while True:
        try:
            time.sleep(POLL_SECONDS)
            tickers = get_tickers(TICKER_URL)
            price = get_price(tickers, symbol)

            log(
                f"{symbol} Current: ${price:,.2f} | "
                f"🔻 Lower: ${lower_threshold:,.2f} | "
                f"🔺 Upper: ${upper_threshold:,.2f}"
            )

            # Check UPWARD movement
            if price >= upper_threshold:
                triggered_level = upper_threshold
                # Advance upper threshold past the current price
                while price >= upper_threshold:
                    upper_threshold += STEP
                # Set lower threshold at a STEP bracket below the triggered level
                lower_threshold = upper_threshold - (2 * STEP)

                alert_text = (
                    f"📈 <b>{symbol} UPWARD ALERT</b>\n\n"
                    f"💵 <b>Current Price:</b> ${price:,.2f}\n"
                    f"🔺 <b>Crossed Level:</b> ${triggered_level:,.2f}\n"
                    f"🎯 <b>Next Targets:</b> 🔺 ${upper_threshold:,.2f} | 🔻 ${lower_threshold:,.2f}\n"
                    f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                    "⚠️ <i>Price alert only — not a trading instruction.</i>"
                )
                log(f"*** UP ALERT TRIGGERED: Price ${price:,.2f} >= ${triggered_level:,.2f} ***")
                send_message(alert_text)
                log(f"New thresholds: 🔻 ${lower_threshold:,.2f} | 🔺 ${upper_threshold:,.2f}")

            # Check DOWNWARD movement
            elif price <= lower_threshold:
                triggered_level = lower_threshold
                # Advance lower threshold down past the current price
                while price <= lower_threshold:
                    lower_threshold -= STEP
                # Set upper threshold at a STEP bracket above the triggered level
                upper_threshold = lower_threshold + (2 * STEP)

                alert_text = (
                    f"📉 <b>{symbol} DOWNWARD ALERT</b>\n\n"
                    f"💵 <b>Current Price:</b> ${price:,.2f}\n"
                    f"🔻 <b>Crossed Level:</b> ${triggered_level:,.2f}\n"
                    f"🎯 <b>Next Targets:</b> 🔺 ${upper_threshold:,.2f} | 🔻 ${lower_threshold:,.2f}\n"
                    f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                    "⚠️ <i>Price alert only — not a trading instruction.</i>"
                )
                log(f"*** DOWN ALERT TRIGGERED: Price ${price:,.2f} <= ${triggered_level:,.2f} ***")
                send_message(alert_text)
                log(f"New thresholds: 🔻 ${lower_threshold:,.2f} | 🔺 ${upper_threshold:,.2f}")

        except KeyboardInterrupt:
            log("Bot stopped by user (KeyboardInterrupt).")
            try:
                send_message("🛑 <b>PAXG Price Bot stopped.</b>")
            except Exception:
                pass
            break
        except Exception as exc:
            log(f"Temporary monitoring error: {type(exc).__name__}: {exc}")
            time.sleep(min(POLL_SECONDS * 2, 10))


if __name__ == "__main__":
    main()
