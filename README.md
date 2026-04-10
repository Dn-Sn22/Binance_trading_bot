<div align="center">

# Binance Trading Bot

### Autonomous AI-Powered Swing Trading System for BTC/USDT

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Binance](https://img.shields.io/badge/Binance-WebSocket_API-F0B90B?style=flat-square&logo=binance&logoColor=black)](https://binance.com)
[![Claude](https://img.shields.io/badge/Claude_API-Haiku-CC785C?style=flat-square)](https://anthropic.com)
[![asyncio](https://img.shields.io/badge/asyncio-concurrent-4B8BBE?style=flat-square)](https://docs.python.org/3/library/asyncio.html)
[![Status](https://img.shields.io/badge/Status-Paper_Trading-yellow?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)]()

*A research-grade algorithmic trading system combining statistical anomaly detection with real-time AI sentiment analysis — built to compete with and eventually surpass institutional-grade swing bots.*

</div>

---

## Overview

BTB is a fully autonomous BTC/USDT swing trading bot that runs 24/7 on Binance. It fuses two independent signal streams — a **statistical price anomaly detector** (Z-score on log returns) and a **multi-source AI sentiment engine** (Claude API + live crypto news) — into a single high-confidence entry signal, with a layered risk management system protecting capital at every step.

The project is currently in **paper trading validation phase** on Binance Testnet, accumulating a 70–100 trade dataset for statistical backtesting and parameter optimization. The target benchmark is Binance's native swing bots — with a roadmap toward a multi-strategy, multi-asset platform.

> Built from scratch in Python using asyncio, WebSocket streaming, and the Anthropic Claude API. No trading frameworks — every module is custom-built for full transparency and control.

---

## How It Works

Two independent conditions must align simultaneously to trigger an entry:

```
[Scanner]   Z-score of log returns > 2.0  →  statistical price anomaly detected
[Research]  AI sentiment confidence > 0.70 →  strong directional news signal

         ↓ both conditions met ↓

[Risk]    Kelly Criterion calculates position size
          6-layer capital protection checks pass

         ↓ cleared ↓

[Executor]  Limit order placed on Binance
[Monitor]   Watches position every 3s for TP / SL / reverse-signal exit
```

This dual-confirmation approach filters out noise from either source alone — a strong price signal with neutral news, or strong news with no price anomaly, will not trigger a trade.

---

## Architecture

```
Binance_trading_bot/
├── main.py                # Async orchestrator — runs 3 concurrent tasks
├── config.py              # All parameters in one place
├── requirements.txt
├── .env.example
├── positions.json         # Active positions state
├── risk_state.json        # Persisted risk manager state
│
├── src/
│   ├── scanner.py         # Binance WebSocket + Z-score anomaly detection
│   ├── research.py        # News aggregation + Claude sentiment analysis
│   ├── risk.py            # Kelly Criterion + 6-level capital protection
│   ├── executor.py        # Binance limit orders + stop-loss (testnet)
│   ├── position_monitor.py# Exit logic: TP / SL / reverse-signal (3s loop)
│   └── telegram_bot.py    # Real-time Telegram notifications
│
└── logs/
    ├── main.log
    ├── scanner.log
    ├── research.log
    └── trades.xlsx        # Full trade history with timestamps
```

### Module Details

| Module | Function | Key Technology |
|--------|----------|---------------|
| `scanner.py` | Real-time price stream, Z-score on log returns | Binance WebSocket API |
| `research.py` | News every 5min, AI sentiment scoring | Claude Haiku, CryptoPanic, RSS, Fear & Greed |
| `risk.py` | Position sizing, 6 capital protections | Kelly Criterion, persistent state |
| `executor.py` | Order placement, stop-loss management | Binance REST API (testnet) |
| `position_monitor.py` | Exit conditions checked every 3 seconds | asyncio task |
| `telegram_bot.py` | Trade alerts, status updates | Telegram Bot API |

---

## Signal Engine

### Price Anomaly Detection (scanner.py)
- Streams BTC/USDT tick data via WebSocket
- Computes **Z-score of log returns** on a rolling window
- Triggers signal when `|Z| > 2.0` — statistically significant deviation from recent price behavior
- Passes live WebSocket price directly to executor (no redundant REST calls)

### AI Sentiment Engine (research.py)
Aggregates from 4 independent sources every 5 minutes:

| Source | Type | Rate Limit Handling |
|--------|------|---------------------|
| CryptoPanic API | News aggregator + community votes | Auto-disable at 600/month limit |
| CoinTelegraph RSS | Crypto media | Unlimited |
| CoinDesk RSS | Crypto media | Unlimited |
| Fear & Greed Index | Market sentiment (0–100) | Unlimited |

All sources are fed to **Claude Haiku** for unified sentiment classification: `bullish / bearish / neutral` with a confidence score. Only signals with `confidence ≥ 0.70` are passed forward.

---

## Risk Management

6-layer capital protection system, state persisted to `risk_state.json`:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Position size | max 5% per trade | Kelly Criterion-adjusted |
| Stop-loss | 8% | Hard floor per position |
| Take-profit | 5% | Fixed exit target |
| Max open positions | 10 (paper) / 3 (live) | Concentration limit |
| Daily loss limit | 10% | Shuts off trading for the day |
| Max drawdown | 25% | Full system halt |
| Entry cooldown | 20 min | Prevents overtrading |
| Min confidence | 0.70 | Signal quality filter |
| Kelly fraction | 0.25 | Conservative fractional Kelly |

**Exit logic** (position_monitor.py) checks every 3 seconds:
1. Take-profit hit → close
2. Stop-loss hit → close
3. Reverse signal from research → close early

---

## Tech Stack

```
Core          Python 3.11, asyncio, Anaconda (botenv)
Exchange      Binance WebSocket API, Binance REST API (testnet)
AI / NLP      Anthropic Claude API (Haiku) — sentiment analysis
Data          CryptoPanic API, CoinTelegraph RSS, CoinDesk RSS
              Alternative.me Fear & Greed Index
Strategy      Z-score of log returns, Kelly Criterion
Alerts        Telegram Bot API
Logging       Excel trade log (openpyxl), rotating file logs
Environment   Anaconda, python-dotenv
```

---

## Installation

Requires [Anaconda](https://www.anaconda.com/download).

```bash
git clone https://github.com/Dn-Sn22/Binance_trading_bot.git
cd Binance_trading_bot

conda create -n botenv python=3.11 -y
conda activate botenv
conda install pandas numpy -y
pip install -r requirements.txt

cp .env.example .env
# Fill in your API keys: Binance Testnet, Anthropic, CryptoPanic, Telegram
```

**Required API keys** (all free tiers sufficient for paper trading):
- Binance Testnet API key + secret
- Anthropic API key
- CryptoPanic API token
- Telegram Bot token + chat ID

---

## Usage

```bash
conda activate botenv
cd Binance_trading_bot

# Remove stale state before each session
del risk_state.json   # Windows
# rm risk_state.json  # Linux/Mac

python main.py
```

The bot will start 3 concurrent async tasks: price scanning, news research, and position monitoring. All activity is logged and Telegram notifications are sent on trades and alerts.

---

## Current Status & Validation

| Phase | Status |
|-------|--------|
| Core architecture | ✅ Complete |
| Scanner (Z-score) | ✅ Complete |
| Research (AI sentiment) | ✅ Complete |
| Risk management (6-layer) | ✅ Complete |
| Executor (testnet orders) | ✅ Complete |
| Exit logic (TP/SL/reverse) | ✅ Complete |
| Telegram notifications | ✅ Complete |
| Paper trading validation | 🔄 In progress (~40/100 trades) |
| Backtesting & optimization |  Next |
| Telegram upgrade (summaries) |  Planned |
| TUI dashboard (Textual) |  Planned |

---

## Roadmap

### Near-Term
- [ ] **Backtesting framework** — Vectorbt-based parameter sweep across Z-score thresholds, TP/SL ratios, and sentiment weights. Walk-forward validation on 2021–2024 data
- [ ] **Parameter optimization** — Grid search across key variables, Sharpe Ratio and Calmar Ratio as primary optimization targets
- [ ] **Telegram upgrade** — End-of-session summaries, P&L reports, TP selector (3–20% + dynamic), balance-aware sizing
- [ ] **TUI dashboard** — Real-time terminal interface via Textual: live prices, open positions, session stats

### Long-Term Vision

Demiurg is the foundation of a larger platform:

- [ ] **Multi-strategy engine** — Modular strategy switching: swing, scalping, mean-reversion, momentum
- [ ] **Multi-asset expansion** — ETH, SOL, and top-cap altcoins alongside BTC
- [ ] **Multi-agent architecture** — Specialized AI agents per signal type (price, sentiment, on-chain), coordinated by a meta-agent
- [ ] **Web frontend** — Real-time dashboard: portfolio overview, trade history, live signals, performance analytics
- [ ] **On-chain data integration** — Whale wallet tracking, exchange inflows/outflows, funding rates
- [ ] **Live trading deployment** — Full transition from testnet after backtesting validation and 100-trade paper dataset confirmed profitable

---

## Performance Targets

The primary benchmark is Binance's native swing trading bots. Key metrics tracked:

| Metric | Target |
|--------|--------|
| Win rate | > 55% |
| Sharpe Ratio | > 1.5 |
| Max Drawdown | < 15% |
| Monthly return | > 8% |
| Avg R:R ratio | > 1 : 1.5 |

---

## Security

- `DRY_RUN = True` — no real orders placed until manually enabled
- `TRADING_MODE = testnet` — all execution on Binance Testnet
- API keys stored in `.env`, never committed (`.gitignore`)
- `.env.example` provided with placeholder values only

---

## Contributing

The project is moving toward open collaboration. If you're interested in:
- Quantitative strategy development
- ML/AI signal enhancement
- Frontend or infrastructure

Feel free to open an issue or reach out directly.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

*Built with Python, asyncio, and a long-term vision.*
*Currently in research phase — not financial advice.*

</div>
