import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import json
import hashlib
import krakenex

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {"cash": 10000.0, "shares": 0.0}

if "logs" not in st.session_state:
    st.session_state.logs = []

if "symbol" not in st.session_state:
    st.session_state.symbol = "AAPL"

if "portfolio_history" not in st.session_state:
    st.session_state.portfolio_history = []

if "trade_points" not in st.session_state:
    st.session_state.trade_points = []

# -----------------------------
# DATA FETCH
# -----------------------------
def fetch_data(symbol):
    return yf.download(symbol, period="3mo", interval="1d")

# -----------------------------
# INDICATORS
# -----------------------------
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def moving_avg(data, window=20):
    return data['Close'].rolling(window).mean()

# -----------------------------
# AGENTS
# -----------------------------
def analyst_agent(data):
    latest = data.iloc[-1]

    rsi = float(latest['RSI'].item())
    close = float(latest['Close'].item())
    ma = float(latest['MA'].item())

    insights = []

    if rsi < 30:
        insights.append("RSI oversold → BUY")
    elif rsi > 70:
        insights.append("RSI overbought → SELL")

    if close > ma:
        insights.append("Bullish trend")
    else:
        insights.append("Bearish trend")

    return insights, rsi, close, ma

def decision_agent(rsi, close, ma):
    if rsi < 30 and close > ma:
        return "BUY", 80
    elif rsi > 70:
        return "SELL", 75
    return "HOLD", 50

def risk_agent(decision, confidence):
    if confidence < 60:
        return "REJECTED", "Low confidence"
    return "APPROVED", "Valid trade"

# -----------------------------
# KRAKEN
# -----------------------------
def get_kraken():
    k = krakenex.API()
    k.load_key("kraken.key")
    return k

def execute_trade(decision):
    try:
        k = get_kraken()
        side = "buy" if decision == "BUY" else "sell"

        return k.query_private("AddOrder", {
            "pair": "XXBTZUSD",
            "type": side,
            "ordertype": "market",
            "volume": "0.001"
        })
    except Exception as e:
        return str(e)

# -----------------------------
# LOGGING
# -----------------------------
def log_trade(trade):
    trade_str = json.dumps(trade)
    trade["hash"] = hashlib.sha256(trade_str.encode()).hexdigest()

    with open("trade_log.json", "a") as f:
        f.write(json.dumps(trade) + "\n")

# -----------------------------
# UI
# -----------------------------
st.title("🚀 TrustTrade AI")

symbol = st.text_input("Enter Stock Symbol", value=st.session_state.symbol)
st.session_state.symbol = symbol

live_mode = st.checkbox("🚨 Enable Live Trading (Kraken)")

if not live_mode:
    st.success("🧪 Running in Simulation Mode")

# -----------------------------
# RUN AGENT
# -----------------------------
if st.button("Run AI Agent"):

    data = fetch_data(symbol)

    if data.empty:
        st.error("Invalid symbol")
        st.stop()

    # Indicators
    data['RSI'] = calculate_rsi(data)
    data['MA'] = moving_avg(data)
    data = data.dropna().reset_index(drop=True)

    latest_price = float(data.iloc[-1]['Close'].item())

    # PIPELINE
    st.subheader("🧠 AI Pipeline")
    st.dataframe(data.tail())

    insights, rsi, close, ma = analyst_agent(data)
    decision, confidence = decision_agent(rsi, close, ma)
    risk_status, risk_reason = risk_agent(decision, confidence)

    st.write("Insights:", insights)
    st.write("Decision:", decision)
    st.write("Risk:", risk_status)

    # EXECUTION
    if risk_status == "APPROVED":

        if decision == "BUY":
            st.session_state.portfolio["shares"] = st.session_state.portfolio["cash"] / latest_price
            st.session_state.portfolio["cash"] = 0

        elif decision == "SELL":
            st.session_state.portfolio["cash"] = st.session_state.portfolio["shares"] * latest_price
            st.session_state.portfolio["shares"] = 0

        if live_mode:
            res = execute_trade(decision)
            st.write("📡 Kraken:", res)

    # PORTFOLIO
    portfolio_value = (
        st.session_state.portfolio["cash"]
        + st.session_state.portfolio["shares"] * latest_price
    )

    st.subheader("💰 Portfolio")
    st.write(f"Value: ${portfolio_value:.2f}")

    # STORE HISTORY (FIXED)
    st.session_state.portfolio_history.append({
        "time": datetime.now(),
        "symbol": symbol,
        "portfolio_value": portfolio_value
    })

    st.session_state.trade_points.append({
        "time": datetime.now(),
        "symbol": symbol,
        "price": latest_price,
        "action": decision
    })

    # LOG
    trade = {
        "time": str(datetime.now()),
        "symbol": symbol,
        "decision": decision,
        "confidence": confidence,
        "risk": risk_status,
        "price": latest_price,
        "reason": insights
    }

    st.session_state.logs.append(trade)
    log_trade(trade)

# -----------------------------
# 📈 PnL GRAPH (FIXED)
# -----------------------------
st.subheader("📈 Portfolio PnL")

if len(st.session_state.portfolio_history) > 1:

    df_pnl = pd.DataFrame(st.session_state.portfolio_history)
    df_pnl = df_pnl.sort_values("time")

    df_pnl = df_pnl.pivot(index="time", columns="symbol", values="portfolio_value")

    st.line_chart(df_pnl)

else:
    st.info("Run more trades to see PnL")

# -----------------------------
# 📊 TRADE HISTORY
# -----------------------------
st.subheader("📊 Trade History")

if len(st.session_state.trade_points) > 0:
    df_trades = pd.DataFrame(st.session_state.trade_points)
    st.dataframe(df_trades)
else:
    st.info("No trades yet")

# -----------------------------
# 📜 LOGS
# -----------------------------
st.subheader("📜 Logs")

if len(st.session_state.logs) == 0:
    st.info("No logs yet")
else:
    for log in reversed(st.session_state.logs[-5:]):
        st.json(log)

# -----------------------------
# RESET BUTTON (OPTIONAL)
# -----------------------------
if st.button("🔄 Reset Data"):
    st.session_state.portfolio_history = []
    st.session_state.trade_points = []
    st.session_state.logs = []