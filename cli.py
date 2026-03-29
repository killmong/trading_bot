import argparse, os, sys, logging
from dotenv import load_dotenv
from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import place_order

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")
setup_logging()
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot")
    parser.add_argument("--symbol",   required=True,  help="e.g. BTCUSDT")
    parser.add_argument("--side",     required=True,  choices=["BUY", "SELL"])
    parser.add_argument("--type",     required=True,  choices=["MARKET", "LIMIT"], dest="order_type")
    parser.add_argument("--quantity", required=True,  help="e.g. 0.01")
    parser.add_argument("--price",    required=False, help="Required for LIMIT orders")
    args = parser.parse_args()

    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        print("[ERROR] Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file")
        sys.exit(1)

    print(f"\n{'─'*50}")
    print(f"  Order Request")
    print(f"{'─'*50}")
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side}")
    print(f"  Type       : {args.order_type}")
    print(f"  Quantity   : {args.quantity}")
    if args.price:
        print(f"  Price      : {args.price}")
    print(f"{'─'*50}\n")

    try:
        client   = BinanceClient(api_key, api_secret)
        response = place_order(client, args.symbol, args.side,
                               args.order_type, args.quantity, args.price)

        print(f"{'─'*50}")
        print(f"  Order Response")
        print(f"{'─'*50}")
        print(f"  Order ID     : {response.get('orderId', 'N/A')}")
        print(f"  Status       : {response.get('status', 'N/A')}")
        print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
        print(f"  Avg Price    : {response.get('avgPrice', 'N/A')}")
        print(f"{'─'*50}")
        print(f"\n  SUCCESS — Order placed!\n")
        logger.info("Order placed successfully | orderId=%s status=%s",
                    response.get('orderId'), response.get('status'))
    except Exception as e:
        print(f"\n  FAILED — {e}\n")
        logger.error("Order failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
