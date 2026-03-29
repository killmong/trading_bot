# Binance Futures Testnet Trading Bot

A Python trading bot built on Binance Futures Testnet (USDT-M) as a learning project.
Includes an interactive CLI and a Streamlit web dashboard.

> Built while learning Python. I came across Binance Futures Testnet — a sandbox where
> you can place fake trades with no real money — and thought it would be a great way to
> learn how REST APIs, request signing, and trading systems work in practice.
> Claude AI was used to help design and build this project.

---

## What I Learned Building This

- How authenticated REST APIs work (headers, signing, timestamps)
- HMAC-SHA256 request signing — Binance requires every request to be signed with your secret key
- Why separating concerns (API layer vs UI layer) makes code easier to extend
- How to read and use API documentation
- Structured logging and proper error handling in Python
- Building interactive CLI tools with `argparse`
- Building a web UI quickly with Streamlit

---

## Features

- Place **Market** and **Limit** orders on Binance Futures Testnet
- Supports both **BUY** and **SELL** sides
- **Interactive CLI** — guides you step by step with validation at every input
- **Streamlit Web UI** — dark trading terminal dashboard in the browser
- Structured logging of every API request, response, and error to a log file
- Clean two-layer architecture — API layer (`bot/`) and UI layer (`cli.py` / `app.py`)
- Full exception handling for invalid inputs, API errors, and network failures

---

## Project Structure

```
trading_bot/
  bot/
    __init__.py          # Marks bot/ as a Python package
    client.py            # Binance API client — handles signing & HTTP requests
    orders.py            # Order placement logic
    validators.py        # Input validation
    logging_config.py    # File + console logging setup
  logs/
    trading_bot.log      # All requests, responses, errors logged here
  cli.py                 # Interactive CLI entry point
  app.py                 # Streamlit web UI
  .env                   # Your API credentials (never commit this)
  .gitignore
  requirements.txt
  README.md
```

---

## How It Works

### Two Layer Architecture

```
User Input (CLI or Web UI)
        │
        ▼
   validators.py  ← checks all inputs before any API call
        │
        ▼
    orders.py     ← builds correct params for each order type
        │
        ▼
    client.py     ← signs request with HMAC-SHA256 + sends to Binance
        │
        ▼
POST https://testnet.binancefuture.com/fapi/v1/order
        │
        ▼
Response printed to UI + logged to trading_bot.log
```

### How Request Signing Works

Binance requires every authenticated request to be signed. Here's what happens in `client.py`:

1. A `timestamp` (Unix milliseconds) is added to the params
2. All params are URL-encoded into a query string
3. An HMAC-SHA256 hash is created from the query string using your API secret
4. The `signature` is appended to the params
5. Your API key is sent in the `X-MBX-APIKEY` header

This is what makes the request trusted by Binance — without a valid signature every request returns a 401 error.

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign in with your GitHub account
3. Go to the **API Key** section and generate a key pair
4. Copy your API Key and Secret Key

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/trading-bot.git
cd trading_bot
```

### 3. Create a Virtual Environment

```powershell
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Add Your API Keys

Open `.env` and fill in your testnet credentials:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

> ⚠️ Never commit your `.env` file. It is already excluded via `.gitignore`.

---

## How to Run

### Option A — Interactive CLI

```powershell
python cli.py
```

The bot will guide you through everything step by step:

```
============================================================
   Binance Futures Testnet Trading Bot
============================================================

  Connected to Binance Futures Testnet

  Available symbols: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT
  Enter symbol (e.g. BTCUSDT): BTCUSDT
  Enter side   (BUY / SELL): BUY
  Enter type   (MARKET / LIMIT): MARKET
  Enter quantity (e.g. 0.01): 0.01

  ────────────────────────────────────────────────────────
  Order Summary
  ────────────────────────────────────────────────────────
  Symbol      : BTCUSDT
  Side        : BUY
  Type        : MARKET
  Quantity    : 0.01
  ────────────────────────────────────────────────────────

  Confirm order? (YES / NO): YES

  ✓ SUCCESS — Order placed!
```

Press `Ctrl+C` at any time to exit cleanly.

### Option B — Streamlit Web UI

```powershell
streamlit run app.py
```

Opens a web dashboard at `http://localhost:8501` automatically with:

- Symbol, side, order type and quantity inputs
- Live order preview before placing
- Color coded success and error response cards
- Order history table

---

## Order Types

| Type     | Description                                  | Price Required |
| -------- | -------------------------------------------- | -------------- |
| `MARKET` | Executes immediately at current market price | No             |
| `LIMIT`  | Executes only when market reaches your price | Yes            |

---

## Logging

All activity is automatically saved to `logs/trading_bot.log`.

Example log output:

```
2026-03-29 10:45:01 | DEBUG | bot.client | POST https://testnet.binancefuture.com/fapi/v1/order
2026-03-29 10:45:02 | INFO  | bot.orders | Placing MARKET BUY order | symbol=BTCUSDT qty=0.01
2026-03-29 10:45:02 | INFO  | __main__   | Order placed successfully | orderId=123456 status=FILLED
```

The log file rotates automatically at 5MB and keeps the last 3 backups.

---

## Dependencies

```
requests>=2.31.0       # HTTP client for Binance API calls
python-dotenv>=1.0.0   # Loads API keys from .env
streamlit>=1.32.0      # Web UI dashboard
```

---

## Want to Extend This?

Some ideas if you want to build on top of this:

- Add more order types (Stop-Market, OCO)
- Add account balance display using `GET /fapi/v2/balance`
- Add open positions viewer using `GET /fapi/v2/positionRisk`
- Add live price feed using Binance WebSocket
- Add a simple trading strategy (Moving Average crossover, RSI)
- Switch from testnet to live Binance API (just change the base URL and use real credentials)

---

## Built With

- [Python 3.x](https://python.org)
- [Binance Futures Testnet](https://testnet.binancefuture.com)
- [Streamlit](https://streamlit.io)
- [Claude AI](https://claude.ai) — used to help design and build this project

---

## Disclaimer

This project uses the **Binance Futures Testnet only** — no real money is involved.
Do not use this with live Binance credentials without fully understanding the risks of futures trading.
