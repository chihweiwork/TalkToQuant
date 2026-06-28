import os
from pathlib import Path

import requests
import pandas as pd

API_BASE = "https://api.finmindtrade.com/api/v4"
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _load_dotenv():
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def _get_token() -> str:
    _load_dotenv()
    token = os.environ.get("FINMIND_TOKEN")
    if not token:
        raise RuntimeError(
            "FINMIND_TOKEN 未設定。請先執行：\n"
            '  export FINMIND_TOKEN="your_token_here"\n'
            "至 https://finmindtrade.com/ 註冊取得 token。"
        )
    return token


def _fetch(dataset: str, params: dict) -> pd.DataFrame:
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_BASE}/data", params={"dataset": dataset, **params}, headers=headers)

    if resp.status_code == 402:
        raise RuntimeError("API 用量超出上限 (HTTP 402)，請稍後再試或升級方案。")

    data = resp.json()
    if data.get("status") != 200:
        raise RuntimeError(f"FinMind API 錯誤：{data.get('msg', '未知錯誤')}")

    rows = data.get("data", [])
    if not rows:
        raise RuntimeError(
            f"查無資料。dataset={dataset}, params={params}\n"
            "可能原因：data_id 錯誤、日期範圍無交易日、或需要更高會員等級。"
        )

    return pd.DataFrame(rows)


def fetch_stock_data(stock_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = _fetch("TaiwanStockPrice", {
        "data_id": stock_id,
        "start_date": start_date,
        "end_date": end_date,
    })
    df["date"] = pd.to_datetime(df["date"])
    for col in ["open", "close", "max", "min"]:
        df[col] = df[col].astype(float)
    df["Trading_Volume"] = df["Trading_Volume"].astype(int)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def fetch_benchmark(start_date: str, end_date: str) -> pd.DataFrame:
    df = _fetch("TaiwanStockTotalReturnIndex", {
        "data_id": "TAIEX",
        "start_date": start_date,
        "end_date": end_date,
    })
    df["date"] = pd.to_datetime(df["date"])
    df["price"] = df["price"].astype(float)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def lookup_stock_id(stock_name: str) -> str:
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{API_BASE}/data",
        params={"dataset": "TaiwanStockInfo"},
        headers=headers,
    )
    data = resp.json()
    if data.get("status") != 200:
        raise RuntimeError(f"查詢股票代號失敗：{data.get('msg')}")

    for row in data.get("data", []):
        if stock_name in row.get("stock_name", ""):
            return row["stock_id"]

    raise RuntimeError(f"找不到名稱包含「{stock_name}」的股票。")
