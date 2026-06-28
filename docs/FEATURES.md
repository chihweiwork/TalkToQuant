# TalkToQuant 功能清單

> 最後更新：2026-06-27

## 📊 專案概述

TalkToQuant 是一個**自然語言驅動的台股量化回測系統**，整合 FinMind API，支援從策略發想到回測報告的完整工作流程。

---

## ✅ 已完成功能

### 一、資料層 (`backtest/data.py`)

#### 1.1 FinMind API 整合
- ✅ 台股股價資料查詢 (`fetch_stock_data`)
  - 支援股票代號查詢（如 2330）
  - 自訂日期區間
  - 自動格式轉換（日期、價格、成交量）
  
- ✅ 大盤指數查詢 (`fetch_benchmark`)
  - TAIEX 加權指數
  - 用於策略績效比較
  
- ✅ 股票代號查詢 (`lookup_stock_id`)
  - 支援中文股票名稱查詢（如「台積電」→「2330」）
  - 模糊匹配

#### 1.2 錯誤處理
- ✅ API 限額偵測（HTTP 402）
- ✅ Token 未設定提示
- ✅ 無資料警告（股票代號錯誤、日期範圍無交易）

**技術實作**：
```python
df = fetch_stock_data("2330", "2024-01-01", "2026-06-27")
# 返回：date, open, close, max, min, Trading_Volume
```

---

### 二、技術指標層 (`backtest/indicators.py`)

#### 2.1 移動平均線 (MA)
- ✅ 任意週期計算 (`add_ma`)
- ✅ 常用組合：5/10/20/60/120 日

#### 2.2 相對強弱指標 (RSI)
- ✅ 標準 14 日 RSI (`add_rsi`)
- ✅ 自訂週期支援

#### 2.3 MACD
- ✅ 快線、慢線、訊號線 (`add_macd`)
- ✅ MACD 柱狀圖（histogram）
- ✅ 預設參數：12/26/9

**技術實作**：
- 純 pandas 實作，無需 ta-lib
- 支援鏈式呼叫：`df = add_ma(df, 5).pipe(add_rsi, 14)`

---

### 三、單一股票回測引擎 (`backtest/engine.py`)

#### 3.1 訊號驅動回測
- ✅ Signal column 規範：
  - `1` = 買入（全部資金）
  - `-1` = 賣出（全部持股）
  - `0` = 持有
  
- ✅ 狀態管理：自動處理買入/賣出邏輯，避免重複買賣

#### 3.2 交易記錄
- ✅ 每筆交易完整記錄：
  - 進場/出場日期與價格
  - 持股數量
  - 單筆損益與報酬率

#### 3.3 績效統計
- ✅ **報酬指標**：
  - 總報酬率
  - 年化報酬率
  
- ✅ **風險指標**：
  - 最大回撤 (Max Drawdown)
  - Sharpe Ratio（無風險利率 1.5%）
  
- ✅ **交易指標**：
  - 勝率
  - 總交易次數
  - 獲利因子 (Profit Factor)

#### 3.4 權益曲線
- ✅ 逐日資產淨值追蹤
- ✅ 支援未平倉部位計算

**回測示例**：
```python
result = run_backtest(df, signal_column="signal", initial_capital=1_000_000)
print(f"總報酬：{result.stats['total_return']*100:.2f}%")
print(f"Sharpe：{result.stats['sharpe_ratio']:.2f}")
```

---

### 四、投資組合回測引擎 (`backtest/portfolio.py`) ⭐ 新增

#### 4.1 多股票組合回測
- ✅ 同時回測多支股票
- ✅ 自訂權重分配（或等權重）
- ✅ 各股獨立策略訊號

#### 4.2 資金管理
- ✅ 初始權重配置
- ✅ 現金與持股分離追蹤
- ✅ 各股獨立買賣邏輯

#### 4.3 績效分析
- ✅ 投資組合總體績效
- ✅ 各股交易明細
- ✅ 分散投資效果評估

**使用範例**：
```python
stocks_data = {
    "2330": df_tsmc,   # 台積電
    "2317": df_foxconn, # 鴻海
    "2454": df_mediatek # 聯發科
}

weights = {"2330": 0.5, "2317": 0.25, "2454": 0.25}

result = run_portfolio_backtest(
    stocks_data=stocks_data,
    weights=weights,
    initial_capital=1_000_000
)
```

---

### 五、報表生成 (`backtest/report.py`)

#### 5.1 終端摘要報告
- ✅ 策略名稱與測試區間
- ✅ 策略 vs 大盤比較
- ✅ Alpha（超額報酬）計算
- ✅ 完整績效統計表
- ✅ 中文格式化輸出

#### 5.2 互動式圖表 (Plotly)
- ✅ 雙子圖佈局：
  - 上圖：策略淨值 vs 大盤（歸一化至 100）
  - 下圖：股價走勢 + 買賣訊號標記
  
- ✅ 圖表特性：
  - 可縮放、拖曳
  - Hover 顯示詳細數據
  - 圖例切換顯示/隱藏
  - 傳統中文文字
  
- ✅ 自動儲存至 `reports/` 目錄
  - 檔名格式：`backtest_{stock_id}_{timestamp}.html`

#### 5.3 報告文字說明
- ✅ 策略表現評價（擊敗/持平/落後大盤）
- ✅ 優化建議提示

**實測數據**：
- 已生成 11+ 份回測報告
- 涵蓋股票：2330, 0050, 2882, 2317, 2454, 3481

---

### 六、自然語言介面 ⭐ 核心特色

#### 6.1 Claude Code Custom Command
- ✅ `/backtest` 命令觸發 (`.claude/commands/backtest.md`)
- ✅ 三階段工作流程：
  1. **解析與識別**：提取股票、日期、策略類型
  2. **互動式確認**：使用 `AskUserQuestion` 詢問參數
  3. **執行回測**：自動生成程式碼並執行

#### 6.2 參數解析
- ✅ 股票識別：
  - 中文名稱（「台積電」）
  - 股票代號（「2330」）
  
- ✅ 日期解析：
  - 相對日期（「過去一年」、「最近兩年」）
  - 絕對日期（「2023年到2024年」）
  
- ✅ 策略類型識別：
  - 均線交叉
  - RSI 超買超賣
  - MACD 交叉
  - 組合條件

#### 6.3 互動式確認 ⭐ 本次改進重點
- ✅ **參數詢問**（使用 `AskUserQuestion` tool）：
  - 短期/長期均線日數（5/10/20, 20/60/120）
  - RSI 參數與門檻值
  - 初始資金（50萬/100萬/200萬）
  
- ✅ **策略合理性檢查**：
  - 矛盾條件偵測（如 RSI < 30 且 RSI > 70）
  - 參數錯誤警告（如短期 = 長期均線）
  - 反向邏輯提示（如 RSI > 70 買入）
  
- ✅ **確認摘要**：執行前顯示完整設定

#### 6.4 回測後建議
- ✅ 提供參數優化方向
- ✅ 策略組合建議
- ✅ 測試期間建議

**使用範例**：
```
使用者：/backtest 回測台積電的均線策略，過去一年

Claude：
✅ 已識別策略類型：均線交叉策略
📋 請確認以下參數：
[顯示互動式問題選項]

使用者：選擇 5 日、20 日、100 萬

Claude：
🎯 回測設定確認：
   - 標的：台積電（2330）
   - 期間：2025-06-27 ~ 2026-06-27
   - 策略：5 日均線 / 20 日均線交叉
   - 初始資金：100 萬

[執行回測並輸出報告]
```

---

### 七、環境診斷 (`backtest/doctor.sh`)

#### 7.1 自動檢查項目
- ✅ uv 套件管理器安裝
- ✅ pyproject.toml 存在
- ✅ 虛擬環境與依賴套件（numpy, pandas, plotly, requests）
- ✅ FINMIND_TOKEN 環境變數設定
- ✅ backtest 模組完整性

#### 7.2 錯誤提示
- ✅ 缺少套件時的安裝指令
- ✅ Token 未設定時的註冊指引

**使用方式**：
```bash
bash /home/chihwei/playground/TalkToQuant/backtest/doctor.sh
```

---

### 八、文檔系統

#### 8.1 使用者文檔
- ✅ `CLAUDE.md`：專案概述、關鍵檔案、API 說明
- ✅ `finmind.md`：FinMind 助手系統提示詞（75+ 資料集參考）
- ✅ `PORTFOLIO_BACKTEST.md`：投資組合回測完整指南
- ✅ `FEATURES.md`：本檔案，功能清單

#### 8.2 開發者文檔
- ✅ `.claude/commands/backtest.md`：回測 command 完整規格
  - 工作流程說明
  - API 參考
  - 策略範例（MA/RSI/MACD/組合）
  - 日期處理規則
  - 完整範例

---

## 📈 實測數據

### 回測案例
- **執行次數**：11+ 次成功回測
- **測試股票**：
  - 2330（台積電）
  - 0050（台灣 50）
  - 2882（國泰金）
  - 2317（鴻海）
  - 2454（聯發科）
  - 3481（群創）

### 策略類型
- ✅ 簡單均線交叉（5/20, 10/60）
- ✅ RSI 超買超賣
- ✅ 動態多因子系統（MA + RSI + MACD）
- ✅ 投資組合策略（多股票組合）

---

## 🎯 完成度評估

根據原始需求：

| 需求項目 | 完成度 | 說明 |
|---------|--------|------|
| 1. 自然語言輸入 | ✅ 100% | 透過 `/backtest <description>` 實現 |
| 2. LLM 確認問題 | ✅ 90% | 使用 `AskUserQuestion` 互動式確認 |
| 3. 自動執行回測 | ✅ 95% | 完整引擎 + 報表 + 圖表 |
| **總體完成度** | **✅ 85-90%** | 核心功能完整，已投入實際使用 |

---

## 🔧 技術架構

### 核心依賴
```toml
[project]
dependencies = [
    "pandas>=2.2.3",
    "requests>=2.32.3",
    "plotly>=5.24.1",
    "numpy>=2.2.1",
]
```

### 模組結構
```
TalkToQuant/
├── backtest/                 # 回測核心模組
│   ├── __init__.py
│   ├── data.py              # FinMind API 資料層
│   ├── indicators.py        # 技術指標
│   ├── engine.py            # 單一股票回測引擎
│   ├── portfolio.py         # 投資組合回測引擎 ⭐ 新增
│   ├── report.py            # 報表與圖表生成
│   └── doctor.sh            # 環境診斷
├── reports/                 # 回測報告輸出目錄
├── .claude/
│   └── commands/
│       └── backtest.md      # 自然語言介面定義
├── CLAUDE.md                # 專案說明
├── finmind.md               # FinMind API 參考
├── PORTFOLIO_BACKTEST.md    # 投資組合指南
└── FEATURES.md              # 本檔案
```

---

## 🚀 使用流程

### 簡單範例
```bash
/backtest 回測台積電的 5/20 均線策略，過去一年
```

### 複雜範例
```python
# 手動撰寫複雜策略
import sys
sys.path.insert(0, "/home/chihwei/playground/TalkToQuant")

from backtest.data import fetch_stock_data
from backtest.indicators import add_ma, add_rsi, add_macd
from backtest.engine import run_backtest

df = fetch_stock_data("2330", "2024-01-01", "2026-06-27")
df = add_ma(df, 10)
df = add_ma(df, 30)
df = add_rsi(df, 14)
df = add_macd(df)

# 自訂策略邏輯
df["signal"] = 0
buy = (df["ma_10"] > df["ma_30"]) & (df["rsi_14"] < 60) & (df["macd"] > 0)
sell = (df["ma_10"] < df["ma_30"]) & (df["rsi_14"] > 65)
df.loc[buy, "signal"] = 1
df.loc[sell, "signal"] = -1

result = run_backtest(df, initial_capital=1_000_000)
```

---

## 📊 改進歷程

### 初版（完成度 65-70%）
- ✅ 回測引擎
- ✅ 基本自然語言介面
- ❌ 無互動確認
- ❌ 無投資組合功能

### 當前版本（完成度 85-90%）
- ✅ 互動式參數確認
- ✅ 策略合理性檢查
- ✅ 投資組合回測
- ✅ 完整文檔

---

## 🔮 未來擴充方向

### 優先級 P1
- [ ] 更多技術指標（布林通道、KD、ATR）
- [ ] 參數優化（Grid Search）
- [ ] 策略比較模式

### 優先級 P2
- [ ] 投資組合再平衡（月度/季度）
- [ ] 風險平價權重計算
- [ ] 效率前緣分析
- [ ] 更多風險指標（Sortino Ratio, Calmar Ratio）

### 優先級 P3
- [ ] 即時資料串流
- [ ] 多因子模型
- [ ] 機器學習策略支援
- [ ] Web UI 介面

---

## 📝 版本資訊

- **版本**：v0.9（Beta）
- **最後更新**：2026-06-27
- **測試狀態**：✅ 已實測 11+ 次回測
- **穩定性**：✅ 生產環境可用

---

## 🤝 貢獻者

- **開發者**：chihwei (chihweiwork@gmail.com)
- **AI 助手**：Claude Sonnet 4.5 (Anthropic)

---

## 📄 授權

請參考專案 LICENSE 檔案。
