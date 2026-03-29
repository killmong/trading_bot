import os, sys, logging
from dotenv import load_dotenv
from pathlib import Path
from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import place_order

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
setup_logging()
logger = logging.getLogger(__name__)

BANNER = """
============================================================
   Binance Futures Testnet Trading Bot
============================================================
"""

VALID_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
VALID_SIDES   = ["BUY", "SELL"]
VALID_TYPES   = ["MARKET", "LIMIT"]

def prompt(message, valid_choices=None):
    while True:
        value = input(f"  {message}: ").strip().upper()
        if not value:
            print(f"  ✗ This field cannot be empty. Please try again.")
            continue
        if valid_choices and value not in valid_choices:
            print(f"  ✗ Invalid choice '{value}'. Must be one of: {', '.join(valid_choices)}")
            continue
        return value

def prompt_number(message):
    while True:
        value = input(f"  {message}: ").strip()
        try:
            if float(value) <= 0:
                print(f"  ✗ Value must be greater than 0.")
                continue
            return value
        except ValueError:
            print(f"  ✗ Invalid number '{value}'. Please enter a valid number.")

def confirm_order(symbol, side, order_type, quantity, price):
    print(f"\n{'─'*60}")
    print(f"  Order Summary")
    print(f"{'─'*60}")
    print(f"  Symbol      : {symbol}")
    print(f"  Side        : {side}")
    print(f"  Type        : {order_type}")
    print(f"  Quantity    : {quantity}")
    if price:
        print(f"  Price       : {price}")
    print(f"{'─'*60}")
    confirm = input("\n  Confirm order? (YES / NO): ").strip().upper()
    return confirm == "YES"

def main():
    print(BANNER)

    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        print("  [ERROR] API keys not found. Please check your .env file.")
        sys.exit(1)

    print(f"  Connected to Binance Futures Testnet\n")

    while True:
        try:
            # ── Step 1: Symbol ───────────────────────────────────────
            print(f"  Available symbols: {', '.join(VALID_SYMBOLS)}")
            symbol = prompt("Enter symbol (e.g. BTCUSDT)", VALID_SYMBOLS)

            # ── Step 2: Side ─────────────────────────────────────────
            side = prompt("Enter side   (BUY / SELL)", VALID_SIDES)

            # ── Step 3: Order Type ───────────────────────────────────
            order_type = prompt("Enter type   (MARKET / LIMIT)", VALID_TYPES)

            # ── Step 4: Quantity ─────────────────────────────────────
            quantity = prompt_number("Enter quantity (e.g. 0.01)")

            # ── Step 5: Price (only for LIMIT) ───────────────────────
            price = None
            if order_type == "LIMIT":
                price = prompt_number("Enter price (USDT)")

            # ── Step 6: Confirm ──────────────────────────────────────
            confirmed = confirm_order(symbol, side, order_type, quantity, price)
            if not confirmed:
                print("\n  ✗ Order cancelled.\n")
            else:
                print(f"\n  Placing your order...\n")
                client   = BinanceClient(api_key, api_secret)
                response = place_order(
                    client, symbol, side, order_type, quantity, price
                )

                print(f"{'─'*60}")
                print(f"  Order Response")
                print(f"{'─'*60}")
                print(f"  Order ID     : {response.get('orderId', 'N/A')}")
                print(f"  Status       : {response.get('status', 'N/A')}")
                print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
                print(f"  Avg Price    : {response.get('avgPrice', 'N/A')}")
                print(f"{'─'*60}")
                print(f"\n  ✓ SUCCESS — Order placed!\n")
                logger.info(
                    "Order placed successfully | orderId=%s status=%s",
                    response.get("orderId"), response.get("status")
                )

        except KeyboardInterrupt:
            print("\n\n  Exiting bot. Goodbye!\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n  ✗ FAILED — {e}\n")
            logger.error("Order failed: %s", e)

        # ── Ask to place another order ────────────────────────────────
        again = input("  Place another order? (YES / NO): ").strip().upper()
        if again != "YES" :
            print("\n  Exiting bot. Goodbye!\n")
            sys.exit(0)
        print()

if __name__ == "__main__":
    main()