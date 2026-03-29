# Binance Futures Testnet Trading Bot

## Setup
1. python -m venv .venv && .venv\Scripts\activate
2. pip install -r requirements.txt
3. Fill in .env with your testnet credentials

## Run Examples
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 80000
