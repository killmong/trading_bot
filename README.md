# Binance Futures Testnet Trading Bot

A Python CLI application that places orders on Binance Futures Testnet (USDT-M) with structured logging, input validation, and clean error handling.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [How to Run](#how-to-run)
- [Order Types](#order-types)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [Assumptions](#assumptions)

---

## Overview

This bot connects to the **Binance Futures Testnet** (no real money involved) and allows you to place trading orders directly from the command line. It supports three order types — Market, Limit, and Stop-Limit — with full input validation and structured logging of every API request and response.

---

## Project Structure

```
trading_bot/
  bot/
    __init__.py          # Marks bot/ as a Python package
    client.py            # Binance API client — handles signing & HTTP requests
    orders.py            # Order placement logic
    validators.py        # Input validation for all CLI arguments
    logging_config.py    # Sets up file + console logging
  logs/
    trading_bot.log      # All requests, responses and errors logged here
  cli.py                 # CLI entry point — run this to place orders
  .env                   # Your API credentials (never commit this)
  .gitignore             # Excludes .env, logs, __pycache__, .venv
  requirements.txt       # Python dependencies
  README.md              # This file
```

---

## How It Works

### Architecture

The project is split into two clear layers:

**1. API Layer (`bot/`)**

Handles all communication with Binance. The user never needs to touch this layer.

- `client.py` — Creates a persistent HTTP session, signs every request using HMAC-SHA256, attaches your API key header, sends the request, and returns the parsed JSON response. All requests and responses are logged at DEBUG level.
- `orders.py` — Builds the correct parameter set for each order type and calls `client.py` to send it.
- `validators.py` — Validates all user inputs before any API call is made. Catches invalid sides, order types, missing prices, and non-positive quantities.
- `logging_config.py` — Configures two log handlers: a rotating file handler (DEBUG level, saves everything to `logs/trading_bot.log`) and a console handler (INFO level, shows clean output in the terminal).

**2. CLI Layer (`cli.py`)**

Handles everything the user sees and types. Uses `argparse` to accept arguments, calls the API layer, and prints a clean formatted summary of the order request and response.

### Request Flow

```
User runs cli.py
      │
      ▼
argparse reads --symbol, --side, --type, --quantity, --price, --stop-price
      │
      ▼
validators.py checks all inputs are valid
      │
      ▼
orders.py builds the correct params dict for the order type
      │
      ▼
client.py signs the request with HMAC-SHA256 + timestamp
      │
      ▼
POST https://testnet.binancefuture.com/fapi/v1/order
      │
      ▼
Response printed to terminal + logged to trading_bot.log
```

### How Request Signing Works

Binance requires every authenticated request to be signed. The signing process in `client.py`:

1. Adds a `timestamp` (Unix milliseconds) to the params
2. URL-encodes all params into a query string
3. Creates an HMAC-SHA256 hash of that query string using your API secret
4. Appends the `signature` to the params
5. Sends your API key in the `X-MBX-APIKEY` header

This ensures Binance can verify the request came from you and has not been tampered with.

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with your GitHub account
3. Navigate to the **API Key** section
4. Generate a new API key and secret
5. Copy both values — you will need them in the next step

### 2. Clone or Download the Project

```bash
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading_bot
```

### 3. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac / Linux
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure Your API Keys

Open the `.env` file and replace the placeholder values:

```
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_API_SECRET=your_actual_api_secret_here
```

> ⚠️ Never commit your `.env` file to GitHub. It is already listed in `.gitignore`.

---

## How to Run

### Basic Syntax

```
python cli.py --symbol SYMBOL --side BUY|SELL --type ORDER_TYPE --quantity QTY [--price PRICE] [--stop-price STOP_PRICE]
```

### Place a Market Order

Executes immediately at the current market price.

```powershell
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a Limit Order

Executes only when the market reaches your specified price.

```powershell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 80000
```

### Place a Stop-Limit Order

Triggers a limit order when the market hits your stop price.

```powershell
python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.01 --price 78000 --stop-price 79000
```

### Example Output

```
──────────────────────────────────────────────────
  Order Request
──────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
──────────────────────────────────────────────────

──────────────────────────────────────────────────
  Order Response
──────────────────────────────────────────────────
  Order ID     : 123456789
  Status       : FILLED
  Executed Qty : 0.01
  Avg Price    : 84250.00
──────────────────────────────────────────────────

  SUCCESS — Order placed!
```

---

## Order Types

| Type       | `--type` value | `--price`    | `--stop-price` | Description                                  |
| ---------- | -------------- | ------------ | -------------- | -------------------------------------------- |
| Market     | `MARKET`       | Not required | Not required   | Fills immediately at market price            |
| Limit      | `LIMIT`        | Required     | Not required   | Fills only at your specified price or better |
| Stop-Limit | `STOP`         | Required     | Required       | Places a limit order when stop price is hit  |

---

## Logging

All activity is logged to `logs/trading_bot.log` automatically.

The log file captures:

- Every API request (endpoint, parameters)
- Every API response (full JSON)
- Validation errors
- Network failures and HTTP errors
- Order success/failure with order ID and status

### Log Format

```
2026-03-29 10:45:01 | DEBUG    | bot.client | POST https://testnet.binancefuture.com/fapi/v1/order params={...}
2026-03-29 10:45:02 | DEBUG    | bot.client | Response: {'orderId': 123456, 'status': 'FILLED', ...}
2026-03-29 10:45:02 | INFO     | bot.orders | Placing MARKET BUY order | symbol=BTCUSDT qty=0.01 price=N/A
2026-03-29 10:45:02 | INFO     | __main__   | Order placed successfully | orderId=123456 status=FILLED
```

The log file rotates automatically at 5MB and keeps the last 3 backups.

---

## Error Handling

The bot handles three categories of errors gracefully:

**Input Validation Errors** — caught before any API call is made:

- Invalid side (not BUY or SELL)
- Invalid order type
- Missing price for LIMIT or STOP orders
- Non-positive quantity

**API Errors** — HTTP errors returned by Binance:

- Invalid API credentials
- Insufficient balance
- Invalid symbol
- Price or quantity outside allowed range

**Network Errors** — connection issues:

- Timeout
- DNS failure
- Connection refused

All errors are printed to the terminal and logged to `trading_bot.log` with full details.

---

## Assumptions

- Uses Binance Futures Testnet only: `https://testnet.binancefuture.com`
- All orders are placed on USDT-M perpetual futures
- Quantity must respect the minimum lot size for the symbol on testnet (0.001 for BTCUSDT)
- Stop-Limit orders use `timeInForce=GTC` (Good Till Cancelled)
- Limit orders use `timeInForce=GTC` (Good Till Cancelled)
- The bot does not manage open positions or cancel existing orders — order placement only
- API keys are loaded from a `.env` file in the same directory as `cli.py`

---

## Dependencies

```
requests>=2.31.0       # HTTP client for API calls
python-dotenv>=1.0.0   # Loads API keys from .env file
```

Install with:

```powershell
pip install -r requirements.txt
```

---

