# 🚀 TrustTrade AI

> A trustless, multi-agent AI trading system that explains, validates, and logs every decision.

---

## 🧠 Overview

Most AI trading systems act as black boxes — they provide BUY/SELL signals without any transparency.

**TrustTrade AI** solves this by introducing a **multi-agent architecture** that ensures:
- Every decision is explainable  
- Every trade is risk-validated  
- Every action is logged and verifiable  

---

## ⚙️ How It Works

The system is built as a pipeline of specialized AI agents:

### 🤖 Analyst Agent
- Analyzes market data using:
  - RSI (Relative Strength Index)
  - Moving Averages
- Generates market insights

### 🧠 Decision Agent
- Decides whether to:
  - BUY
  - SELL
  - HOLD

### 🛡️ Risk Agent
- Validates trades before execution  
- Rejects low-confidence decisions  

### 💸 Execution Layer
- Executes trades using **Kraken API** (optional)  
- Supports both:
  - Simulation mode (default)
  - Live trading mode  

### 🔐 Trust Layer
- Logs every trade with:
  - Decision
  - Confidence
  - Reasoning
- Uses **SHA-256 hashing** for verification  

---

## 📊 Features

- 📈 Portfolio tracking (PnL visualization)
- 📊 Trade history tracking
- 📜 Transparent trade logs
- 🧠 Explainable AI decisions
- 🛡️ Risk-aware execution
- 🔄 Multi-stock support (stocks + crypto)

---

## 🛠️ Tech Stack

- Python  
- Streamlit  
- Kraken API  
- yFinance API  
- Pandas & NumPy  
- SHA-256 (hashing for trust layer)
