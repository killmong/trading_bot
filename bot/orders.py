import logging
from bot.client import BinanceClient
from bot.validators import validate

logger = logging.getLogger(__name__)

ENDPOINT = "/fapi/v1/order"

def place_order(client: BinanceClient, symbol: str, side: str,
                order_type: str, quantity: str, price: str = None) -> dict:
    symbol     = symbol.upper()
    side       = side.upper()
    order_type = order_type.upper()

    validate(symbol, side, order_type, quantity, price)

    params = {
        "symbol":   symbol,
        "side":     side,
        "type":     order_type,
        "quantity": quantity,
    }
    if order_type == "LIMIT":
        params["price"]       = price
        params["timeInForce"] = "GTC"

    logger.info("Placing %s %s order | symbol=%s qty=%s price=%s",
                order_type, side, symbol, quantity, price or "MARKET")
    return client.post(ENDPOINT, params)
