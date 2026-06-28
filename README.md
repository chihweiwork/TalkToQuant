# TalkToQuant

> 用自然語言回測台股策略的 AI 助手

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 一句話介紹

**不用寫程式，用中文描述交易策略，AI 自動執行回測並產生專業報告。**

---

## 為什麼需要 TalkToQuant？

傳統量化回測的三大痛點：

| 傳統回測 | TalkToQuant |
|---------|-------------|
| 需要程式能力（門檻高） | 中文描述即可 |
| 手動調整參數（重複工作） | AI 引導確認 |
| 結果難以比較（缺乏標準） | 標準化專業報告 |
| 只能測單一股票 | 支援投資組合 |

---

## 快速體驗（30 秒）

### 1. 用中文描述策略

```bash
/backtest 回測台積電的 5 日均線和 20 日均線交叉策略，過去一年
```

### 2. AI 互動確認參數

```
已識別策略類型：均線交叉策略
請確認以下參數：
   - 短期均線：5 日
   - 長期均線：20 日
   - 初始資金：100 萬
```

### 3. 30 秒後看到專業報告

- 終端摘要：總報酬、年化報酬、Sharpe Ratio、勝率
- 互動式圖表：資產曲線 vs 大盤、買賣訊號標記
- 自動儲存：HTML 報告可分享

---

## 核心功能

### 自然語言介面
- 用中文描述策略（「回測台積電均線策略」）
- 支援相對日期（「過去一年」、「最近兩年」）
- 自動識別股票名稱（「台積電」→ 2330）

### AI 智能確認
- 互動式參數詢問（避免預設值錯誤）
- 策略合理性檢查（偵測邏輯矛盾）
- 優化建議（回測後提供改進方向）

### 專業回測引擎
- **單一股票回測**：完整交易記錄與權益曲線
- **投資組合回測**：多股票組合、自訂權重分配
- **豐富技術指標**：MA, RSI, MACD（可擴充）
- **完整績效統計**：
  - 報酬指標：總報酬、年化報酬
  - 風險指標：最大回撤、Sharpe Ratio
  - 交易指標：勝率、獲利因子

### 互動式圖表報告
- Plotly 互動圖表（可縮放、Hover 查看詳細資料）
- 雙子圖佈局：策略淨值 vs 大盤 + 買賣訊號
- 自動儲存 HTML（可在瀏覽器中查看）

---

## 安裝與使用

### 環境需求
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) 套件管理器

### 1. 安裝依賴

```bash
cd TalkToQuant
uv pip install pandas requests plotly numpy
```

### 2. 設定 FinMind API Token

前往 [FinMind](https://finmindtrade.com/) 註冊取得免費 API token，然後設定環境變數：

```bash
export FINMIND_TOKEN="your_token_here"
```

或將 token 寫入 `.env` 檔案。

### 3. 執行環境檢查

```bash
bash backtest/doctor.sh
```

### 4. 開始回測

在 Claude Code 中執行：

```bash
/backtest 回測台積電的均線策略，過去一年
```

或手動撰寫 Python 程式：

```python
import sys
sys.path.insert(0, "/path/to/TalkToQuant")

from backtest.data import fetch_stock_data
from backtest.indicators import add_ma
from backtest.engine import run_backtest

df = fetch_stock_data("2330", "2024-01-01", "2026-06-27")
df = add_ma(df, 5)
df = add_ma(df, 20)

df["signal"] = 0
df.loc[df["ma_5"] > df["ma_20"], "signal"] = 1
df.loc[df["ma_5"] < df["ma_20"], "signal"] = -1

result = run_backtest(df, initial_capital=1_000_000)
print(f"總報酬：{result.stats['total_return']*100:.2f}%")
```

---

## 實測數據

- **11+ 次**成功回測
- **6 支股票**測試（2330, 0050, 2882, 2317, 2454, 3481）
- **多種策略**：均線交叉、RSI、MACD、多因子組合、投資組合

**範例回測報告**：查看 `reports/` 目錄

---

## 技術架構

```
┌─────────────────────────────────────────────────────────┐
│               自然語言介面 (Claude Code)                  │
│          "/backtest 回測台積電均線策略"                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   資料層 (data.py)                        │
│           FinMind API → 股價 / 大盤 / 股票查詢              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 指標層 (indicators.py)                    │
│                MA / RSI / MACD                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            回測引擎 (engine.py, portfolio.py)             │
│        單一股票 / 投資組合 → 交易記錄 + 績效統計            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 報表層 (report.py)                        │
│         終端摘要 + Plotly 互動圖表 (HTML)                  │
└─────────────────────────────────────────────────────────┘
```

**核心模組**：
- `backtest/data.py` - FinMind API 整合
- `backtest/indicators.py` - 技術指標計算
- `backtest/engine.py` - 單一股票回測引擎
- `backtest/portfolio.py` - 投資組合回測引擎
- `backtest/report.py` - 報表與圖表生成

---

## 使用範例

### 範例 1：簡單均線策略

```bash
/backtest 回測鴻海的 10 日和 60 日均線交叉策略，過去兩年
```

### 範例 2：RSI 超買超賣策略

手動撰寫程式碼：

```python
from backtest.data import fetch_stock_data
from backtest.indicators import add_rsi
from backtest.engine import run_backtest

df = fetch_stock_data("0050", "2024-01-01", "2026-06-27")
df = add_rsi(df, 14)

df["signal"] = 0
df.loc[df["rsi_14"] < 30, "signal"] = 1   # 超賣買入
df.loc[df["rsi_14"] > 70, "signal"] = -1  # 超買賣出

result = run_backtest(df, initial_capital=1_000_000)
```

### 範例 3：投資組合回測

```python
from backtest.portfolio import run_portfolio_backtest

# 準備 3 支股票資料（各自有獨立策略訊號）
stocks_data = {
    "2330": df_tsmc,   # 台積電（均線策略）
    "2317": df_foxconn, # 鴻海（RSI 策略）
    "2454": df_mediatek # 聯發科（MACD 策略）
}

# 設定權重：台積電 50%、鴻海 25%、聯發科 25%
weights = {"2330": 0.5, "2317": 0.25, "2454": 0.25}

result = run_portfolio_backtest(
    stocks_data=stocks_data,
    weights=weights,
    initial_capital=1_000_000
)

print(f"組合總報酬：{result.stats['total_return']*100:.2f}%")
```

---

## 差異化定位

**vs 傳統回測工具**（如 Backtrader、Zipline）：
- 不用寫程式，自然語言即可
- AI 引導參數設定
- 更簡單的入門門檻

**vs 其他 AI 工具**：
- 專注台股，深度整合 FinMind API
- 完整回測引擎（非玩具級）
- 支援投資組合分析

**vs 純 GUI 回測平台**：
- 開源免費，完全可控
- 可擴充（自訂指標、策略）
- 適合程式進階使用者

---

## 作者

**chihwei** - [chihweiwork@gmail.com](mailto:chihweiwork@gmail.com)

**AI 協作**：Claude Sonnet 4.5 (Anthropic)

---

## 致謝

- [FinMind](https://finmindtrade.com/) - 提供台股資料 API
- [Plotly](https://plotly.com/) - 互動式圖表庫
- [Claude Code](https://claude.ai/code) - 自然語言介面平台

---

**立即開始**：執行 `/backtest` 開始您的第一次回測！
