# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TalkToQuant is a natural-language financial data assistant that queries Taiwan (and some international) market data from the **FinMind API**. It includes a backtesting engine that lets users describe trading strategies in natural language and get performance reports with interactive charts.

## Key Files

- `README.md` — Project homepage with quick start guide and feature overview
- `finmind.md` — System prompt for the FinMind assistant: intent-to-dataset mapping, query patterns, output strategy, chart configuration, and error handling rules
- `llm-full.txt` — Complete FinMind API reference: all 75+ datasets with tiers, parameters, columns, date ranges, and update schedules
- `.claude/commands/backtest.md` — Claude Code custom command (`/backtest`) for natural-language backtesting
- `docs/FEATURES.md` — Complete feature list (8 modules, 10KB+ documentation)
- `docs/PORTFOLIO_BACKTEST.md` — Portfolio backtesting guide
- `docs/DEMO_SCRIPT.md` — Demo presentation script
- `docs/PRESENTATION.md` — Project introduction slides

## Backtesting Engine (`backtest/`)

Use `/backtest` followed by a natural language strategy description. The engine:
1. Parses stock, date range, and strategy from natural language
2. Fetches data via FinMind API
3. Computes indicators and generates buy/sell signals
4. Runs the backtest and compares against TAIEX benchmark
5. Outputs a terminal report + interactive Plotly HTML chart in `reports/`

### Module Structure
- `data.py` — `fetch_stock_data()`, `fetch_benchmark()`, `lookup_stock_id()`
- `indicators.py` — `add_ma()`, `add_rsi()`, `add_macd()` (pure pandas, no ta-lib)
- `engine.py` — `run_backtest(df, signal_column)` → `BacktestResult` with trades, equity curve, stats
- `report.py` — `generate_report()` → terminal summary + Plotly HTML

### Signal Convention
The `signal` column in the DataFrame drives the engine: `1` = buy, `-1` = sell, `0` = hold.

### Dependencies
```bash
uv pip install pandas requests plotly
```

## FinMind API Essentials

- **Base URL:** `https://api.finmindtrade.com/api/v4`
- **Auth:** `Authorization: Bearer {token}` header; token comes from `$FINMIND_TOKEN` env var.
- **Main endpoints:** `GET /data` (most datasets), `GET /datalist`, `GET /translation`.
- **Special endpoints** (don't use `/data`): `TaiwanStockTradingDailyReport`, `TaiwanStockWarrantTradingDailyReport`, `TaiwanStockTradingDailyReportSecIdAgg`, and all snapshot endpoints (`taiwan_stock_tick_snapshot`, `taiwan_futures_snapshot`, `taiwan_options_snapshot`).
- **Rate limits:** Free 600/hr, Backer 1600/hr, Sponsor 6000/hr, SponsorPro 20000/hr. HTTP 402 = quota exceeded.

## Query Pattern

All queries use Python with `requests` + `pandas`. Install packages with `uv pip install`, not `pip`.

## Charts

All chart text (title, axis labels, legend) must be in **Traditional Chinese**. Register a CJK font before plotting:

```python
import matplotlib.font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
plt.rcParams.update({
    "font.family": fm.FontProperties(fname="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc").get_name(),
    "axes.unicode_minus": False,
})
```

Fallback font: `fonts-noto-cjk` at `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`.
