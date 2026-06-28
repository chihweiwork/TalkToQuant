# 投資組合回測指南

## 功能概述

TalkToQuant 現在支援兩種回測模式：

1. **單一股票回測**（原有功能）：使用 `backtest/engine.py`
2. **投資組合回測**（新增功能）：使用 `backtest/portfolio.py`

---

## 一、單一股票回測

適用於測試單一標的的策略表現。

### 使用方式

```bash
/backtest 回測台積電的均線策略，過去一年
```

### 範例：複雜多因子策略

```python
import sys
sys.path.insert(0, "/home/chihwei/playground/TalkToQuant")

from backtest.data import fetch_stock_data, fetch_benchmark
from backtest.indicators import add_ma, add_rsi, add_macd
from backtest.engine import run_backtest
from backtest.report import generate_report

# 抓取資料
df = fetch_stock_data("2330", "2024-01-01", "2026-06-27")

# 計算指標
df = add_ma(df, 10)
df = add_ma(df, 30)
df = add_rsi(df, 14)
df = add_macd(df)

# 複雜策略邏輯
df["signal"] = 0

# 買入條件：趨勢向上 + RSI 未過熱 + MACD 正向
buy = (df["ma_10"] > df["ma_30"]) & (df["rsi_14"] < 60) & (df["macd"] > 0)

# 賣出條件：趨勢向下 + RSI 超買
sell = (df["ma_10"] < df["ma_30"]) & (df["rsi_14"] > 65)

df.loc[buy, "signal"] = 1
df.loc[sell, "signal"] = -1

# 執行回測
result = run_backtest(df, signal_column="signal", initial_capital=1_000_000)
```

**優點**：
- 詳細的個股分析
- 完整的技術指標支援
- 互動式 Plotly 圖表

**限制**：
- 僅能測試單一標的
- 無法模擬分散投資

---

## 二、投資組合回測

支援多股票組合，可設定權重分配。

### 功能特性

✅ 多股票同時回測  
✅ 自訂權重分配  
✅ 分散風險評估  
✅ 各股獨立策略訊號  

### 基本範例：等權重投資組合

```python
import sys
sys.path.insert(0, "/home/chihwei/playground/TalkToQuant")

from datetime import datetime, timedelta
from backtest.data import fetch_stock_data
from backtest.indicators import add_ma
from backtest.portfolio import run_portfolio_backtest

# 準備股票資料（每支股票可以有不同策略）
stocks_data = {}

for stock_id in ["2330", "2317", "2454"]:
    df = fetch_stock_data(stock_id, "2025-01-01", "2026-06-27")
    df = add_ma(df, 5)
    df = add_ma(df, 20)
    
    # 均線交叉策略
    df["signal"] = 0
    df.loc[df["ma_5"] > df["ma_20"], "signal"] = 1
    df.loc[df["ma_5"] < df["ma_20"], "signal"] = -1
    
    stocks_data[stock_id] = df

# 執行投資組合回測（預設等權重）
result = run_portfolio_backtest(
    stocks_data=stocks_data,
    weights=None,  # None = 等權重（各 33.3%）
    initial_capital=1_000_000,
)

# 查看結果
print(f"總報酬：{result.stats['total_return']*100:.2f}%")
print(f"Sharpe Ratio：{result.stats['sharpe_ratio']:.2f}")
```

### 進階範例：自訂權重 + 不同策略

```python
# 設定不同權重
weights = {
    "2330": 0.5,   # 台積電佔 50%
    "2317": 0.25,  # 鴻海佔 25%
    "2454": 0.25,  # 聯發科佔 25%
}

# 準備資料（各股可用不同策略）
stocks_data = {}

# 台積電：均線策略
df_2330 = fetch_stock_data("2330", "2025-01-01", "2026-06-27")
df_2330 = add_ma(df_2330, 5)
df_2330 = add_ma(df_2330, 20)
df_2330["signal"] = 0
df_2330.loc[df_2330["ma_5"] > df_2330["ma_20"], "signal"] = 1
df_2330.loc[df_2330["ma_5"] < df_2330["ma_20"], "signal"] = -1
stocks_data["2330"] = df_2330

# 鴻海：RSI 策略
df_2317 = fetch_stock_data("2317", "2025-01-01", "2026-06-27")
df_2317 = add_rsi(df_2317, 14)
df_2317["signal"] = 0
df_2317.loc[df_2317["rsi_14"] < 30, "signal"] = 1   # 超賣買入
df_2317.loc[df_2317["rsi_14"] > 70, "signal"] = -1  # 超買賣出
stocks_data["2317"] = df_2317

# 聯發科：MACD 策略
df_2454 = fetch_stock_data("2454", "2025-01-01", "2026-06-27")
df_2454 = add_macd(df_2454)
df_2454["signal"] = 0
df_2454.loc[df_2454["macd"] > df_2454["macd_signal"], "signal"] = 1
df_2454.loc[df_2454["macd"] < df_2454["macd_signal"], "signal"] = -1
stocks_data["2454"] = df_2454

# 執行投資組合回測
result = run_portfolio_backtest(
    stocks_data=stocks_data,
    weights=weights,
    initial_capital=1_000_000,
)

# 查看各股交易明細
for stock_id, trades in result.trades.items():
    print(f"\n{stock_id} 交易次數：{len(trades)}")
    for trade in trades[:3]:  # 顯示前 3 筆
        print(f"  {trade['date']}: {trade['action']} {trade['shares']} 股 @ {trade['price']:.2f}")
```

---

## 三、比較表

| 功能 | 單一股票回測 | 投資組合回測 |
|------|------------|------------|
| 股票數量 | 1 | 多支 |
| 權重分配 | N/A | 支援自訂 |
| 策略彈性 | 單一策略 | 各股可用不同策略 |
| 圖表輸出 | ✅ Plotly HTML | ⚠️ 需手動繪製 |
| 風險分散 | ❌ | ✅ |
| 適用場景 | 個股深度分析 | 資產配置模擬 |

---

## 四、常見問題

### Q1：投資組合回測會自動再平衡嗎？

目前版本：**不會**。一旦初始配置完成，各股獨立依訊號買賣，不會調整權重。

未來可擴充 `rebalance` 參數（月度/季度再平衡）。

### Q2：可以混合股票和大盤 ETF 嗎？

可以！只要能從 FinMind API 取得資料的標的都可以加入投資組合（例如 0050）。

### Q3：權重總和必須是 1.0 嗎？

是的。系統會驗證 `sum(weights.values()) == 1.0`。

### Q4：如何比較投資組合 vs 單一股票？

範例：

```python
# 方案 A：100% 台積電
result_single = run_backtest(df_2330, initial_capital=1_000_000)

# 方案 B：台積電 50% + 鴻海 25% + 聯發科 25%
result_portfolio = run_portfolio_backtest(
    stocks_data={"2330": df_2330, "2317": df_2317, "2454": df_2454},
    weights={"2330": 0.5, "2317": 0.25, "2454": 0.25},
    initial_capital=1_000_000,
)

# 比較 Sharpe Ratio（風險調整後報酬）
print(f"單一股票 Sharpe：{result_single.stats['sharpe_ratio']:.2f}")
print(f"投資組合 Sharpe：{result_portfolio.stats['sharpe_ratio']:.2f}")
```

---

## 五、API 參考

### `run_portfolio_backtest()`

```python
def run_portfolio_backtest(
    stocks_data: Dict[str, pd.DataFrame],  # {stock_id: df_with_signal}
    weights: Dict[str, float] = None,      # {stock_id: weight}, None=等權重
    initial_capital: float = 1_000_000,    # 初始資金
    rebalance: str = "none",               # 再平衡策略（暫不支援）
) -> PortfolioResult
```

**返回值 `PortfolioResult`**：
- `equity_curve`：DataFrame，包含每日權益曲線
- `trades`：Dict[str, List]，各股交易記錄
- `stats`：dict，績效統計（total_return, sharpe_ratio, max_drawdown 等）

---

## 六、未來擴充方向

- [ ] 月度/季度自動再平衡
- [ ] 投資組合視覺化圖表（各股權重變化、相關性熱力圖）
- [ ] 資金分批投入策略（定期定額）
- [ ] 風險平價（Risk Parity）權重計算
- [ ] 效率前緣（Efficient Frontier）分析
