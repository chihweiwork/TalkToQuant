# Backtest 命令變更說明

## 變更內容

移除了 `doctor.sh` 環境檢查步驟，改用 `uv run` 自動處理虛擬環境。

## 原因

1. **doctor.sh 常常失敗**：因為虛擬環境需要手動 source activate
2. **uv run 更可靠**：自動處理虛擬環境啟動
3. **更簡潔**：不需要複雜的環境檢查腳本

## 新的執行方式

### ✅ 正確做法
```bash
cd /home/chihwei/playground/TalkToQuant
uv run python your_script.py
```

### ❌ 錯誤做法
```bash
python your_script.py  # 會找不到 backtest 模組
source .venv/bin/activate && python your_script.py  # 不需要手動 activate
```

## 測試驗證

```bash
# 測試 1: 驗證 imports
uv run python -c "from backtest.data import fetch_stock_data; print('OK')"

# 測試 2: 驗證完整模組
uv run python -c "
from backtest.data import fetch_stock_data, fetch_benchmark, lookup_stock_id
from backtest.indicators import add_ma, add_rsi, add_macd
from backtest.engine import run_backtest
from backtest.report import generate_report
print('✅ All modules loaded')
"
```

## 文件更新

已更新 `/backtest` 命令文檔：
- 移除 "Pre-flight Check" 區塊
- 新增 "Python Execution (REQUIRED)" 區塊
- 更新所有範例代碼使用 `uv run`
- 移除 `sys.path.insert()` 相關說明

## doctor.sh 狀態

`backtest/doctor.sh` 檔案已**標記為廢棄**，但暫時保留以供參考。
未來版本可以安全刪除。
