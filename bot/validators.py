VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT", "STOP"}

def validate(symbol, side, order_type, quantity, price):
    if not symbol:
        raise ValueError("symbol cannot be empty")
    if side.upper() not in VALID_SIDES:
        raise ValueError(f"side must be one of {VALID_SIDES}")
    if order_type.upper() not in VALID_TYPES:
        raise ValueError(f"order_type must be one of {VALID_TYPES}")
    if float(quantity) <= 0:
        raise ValueError("quantity must be positive")
    if order_type.upper() in {"LIMIT", "STOP"} and (price is None or float(price) <= 0):
        raise ValueError("price is required and must be positive for LIMIT/STOP orders")
