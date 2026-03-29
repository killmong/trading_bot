import os, sys, logging
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import place_order

setup_logging()
logger = logging.getLogger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Binance Futures Bot",
    page_icon="📈",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
}

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #f0b90b22;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.header-banner h1 {
    color: #f0b90b;
    font-size: 1.8rem;
    margin: 0;
    letter-spacing: -1px;
}

.header-banner p {
    color: #64748b;
    margin: 0.5rem 0 0;
    font-size: 0.85rem;
    font-family: 'Space Mono', monospace;
}

/* Status badge */
.status-badge {
    display: inline-block;
    background: #052e16;
    color: #4ade80;
    border: 1px solid #166534;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    margin-top: 0.75rem;
}

/* Cards */
.order-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.order-card h3 {
    color: #f0b90b;
    font-size: 0.9rem;
    margin: 0 0 1rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Success box */
.success-box {
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
}

.success-box h3 {
    color: #4ade80;
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    margin: 0 0 1rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.response-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #14532d22;
    font-size: 0.875rem;
}

.response-row:last-child { border-bottom: none; }
.response-label { color: #64748b; }
.response-value { color: #e2e8f0; font-family: 'Space Mono', monospace; font-weight: 700; }

/* Error box */
.error-box {
    background: #1c0a0a;
    border: 1px solid #7f1d1d;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
    color: #f87171;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
}

/* History item */
.history-item {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 0.875rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
}

.history-symbol { color: #f0b90b; font-family: 'Space Mono', monospace; font-weight: 700; }
.history-side-buy  { color: #4ade80; font-weight: 600; }
.history-side-sell { color: #f87171; font-weight: 600; }
.history-status { color: #64748b; font-family: 'Space Mono', monospace; }
.history-time { color: #475569; font-size: 0.75rem; }

/* Streamlit overrides */
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stRadio"] label {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 500 !important;
}

div[data-testid="stSelectbox"] > div > div,
div[data-testid="stNumberInput"] > div > div > input {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

.stButton > button {
    background: #f0b90b !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    letter-spacing: 1px !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

div[data-testid="stRadio"] > div {
    flex-direction: row !important;
    gap: 1rem !important;
}

.stDivider { border-color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "order_history" not in st.session_state:
    st.session_state.order_history = []

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "last_error" not in st.session_state:
    st.session_state.last_error = None

# ── API keys ──────────────────────────────────────────────────────────────────
api_key    = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
connected  = bool(api_key and api_secret)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-banner">
    <h1>📈 Binance Futures Bot</h1>
    <p>USDT-M Testnet · REST API</p>
    <div class="status-badge">{'● CONNECTED' if connected else '● DISCONNECTED'}</div>
</div>
""", unsafe_allow_html=True)

if not connected:
    st.error("API keys not found. Please check your .env file.")
    st.stop()

# ── Order Form ────────────────────────────────────────────────────────────────
st.markdown('<div class="order-card"><h3>Place Order</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    symbol = st.selectbox(
        "Symbol",
        ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    )

with col2:
    order_type = st.selectbox(
        "Order Type",
        ["MARKET", "LIMIT"]
    )

side = st.radio("Side", ["BUY", "SELL"], horizontal=True)

col3, col4 = st.columns(2)

with col3:
    quantity = st.number_input(
        "Quantity",
        min_value=0.001,
        value=0.01,
        step=0.001,
        format="%.3f"
    )

with col4:
    price = None
    if order_type == "LIMIT":
        price = st.number_input(
            "Price (USDT)",
            min_value=1.0,
            value=80000.0,
            step=100.0,
            format="%.2f"
        )
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Market orders execute at current price")

st.markdown('</div>', unsafe_allow_html=True)

# ── Order Summary ─────────────────────────────────────────────────────────────
with st.expander("Order Preview", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Symbol", symbol)
    c2.metric("Side", side)
    c3.metric("Type", order_type)
    c4.metric("Qty", f"{quantity:.3f}")
    if price:
        st.metric("Price", f"${price:,.2f}")

# ── Place Order Button ────────────────────────────────────────────────────────
if st.button(f"🚀 PLACE {side} ORDER"):
    if order_type == "LIMIT" and (not price or price <= 0):
        st.error("Price is required for LIMIT orders.")
    else:
        with st.spinner("Sending order to Binance..."):
            try:
                client   = BinanceClient(api_key, api_secret)
                response = place_order(
                    client,
                    symbol,
                    side,
                    order_type,
                    str(quantity),
                    str(price) if price else None
                )
                st.session_state.last_response = response
                st.session_state.last_error    = None

                # Save to history
                st.session_state.order_history.insert(0, {
                    "orderId":     response.get("orderId", "N/A"),
                    "symbol":      symbol,
                    "side":        side,
                    "type":        order_type,
                    "quantity":    quantity,
                    "price":       price,
                    "status":      response.get("status", "N/A"),
                    "executedQty": response.get("executedQty", "N/A"),
                    "avgPrice":    response.get("avgPrice", "N/A"),
                    "time":        datetime.now().strftime("%H:%M:%S"),
                })

                logger.info("Order placed via UI | orderId=%s status=%s",
                            response.get("orderId"), response.get("status"))

            except Exception as e:
                st.session_state.last_error    = str(e)
                st.session_state.last_response = None
                logger.error("Order failed via UI: %s", e)

# ── Response Display ──────────────────────────────────────────────────────────
if st.session_state.last_response:
    r = st.session_state.last_response
    st.markdown(f"""
    <div class="success-box">
        <h3>✓ Order Placed Successfully</h3>
        <div class="response-row">
            <span class="response-label">Order ID</span>
            <span class="response-value">{r.get('orderId', 'N/A')}</span>
        </div>
        <div class="response-row">
            <span class="response-label">Status</span>
            <span class="response-value">{r.get('status', 'N/A')}</span>
        </div>
        <div class="response-row">
            <span class="response-label">Executed Qty</span>
            <span class="response-value">{r.get('executedQty', 'N/A')}</span>
        </div>
        <div class="response-row">
            <span class="response-label">Avg Price</span>
            <span class="response-value">{r.get('avgPrice', 'N/A')} USDT</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.last_error:
    st.markdown(f"""
    <div class="error-box">
        ✗ ORDER FAILED<br><br>
        {st.session_state.last_error}
    </div>
    """, unsafe_allow_html=True)

# ── Order History ─────────────────────────────────────────────────────────────
if st.session_state.order_history:
    st.divider()
    st.markdown("### 📋 Order History")

    for order in st.session_state.order_history:
        side_class = "history-side-buy" if order["side"] == "BUY" else "history-side-sell"
        st.markdown(f"""
        <div class="history-item">
            <span class="history-symbol">{order['symbol']}</span>
            <span class="{side_class}">{order['side']}</span>
            <span style="color:#94a3b8">{order['type']}</span>
            <span style="color:#e2e8f0;font-family:'Space Mono',monospace">{order['quantity']:.3f}</span>
            <span class="history-status">{order['status']}</span>
            <span class="history-time">{order['time']}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Clear History"):
        st.session_state.order_history = []
        st.session_state.last_response = None
        st.session_state.last_error    = None
        st.rerun()