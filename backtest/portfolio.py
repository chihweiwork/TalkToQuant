"""
投資組合回測引擎
支援多股票組合，可設定權重分配策略
"""
from dataclasses import dataclass, field
from typing import Dict, List
import pandas as pd
import numpy as np


@dataclass
class PortfolioResult:
    """投資組合回測結果"""
    holdings: pd.DataFrame = field(default_factory=pd.DataFrame)  # 持倉明細
    equity_curve: pd.DataFrame = field(default_factory=pd.DataFrame)  # 總權益曲線
    trades: Dict[str, List] = field(default_factory=dict)  # 各股票交易記錄
    stats: dict = field(default_factory=dict)  # 績效統計


def run_portfolio_backtest(
    stocks_data: Dict[str, pd.DataFrame],
    weights: Dict[str, float] = None,
    initial_capital: float = 1_000_000,
    rebalance: str = "none",  # "none", "monthly", "quarterly"
) -> PortfolioResult:
    """
    投資組合回測

    Args:
        stocks_data: {stock_id: df_with_signal, ...}
        weights: {stock_id: weight, ...} 權重總和應為 1.0，None = 等權重
        initial_capital: 初始資金
        rebalance: 再平衡策略
    """

    # 驗證輸入
    if not stocks_data:
        raise ValueError("至少需要一支股票")

    stock_ids = list(stocks_data.keys())

    # 預設等權重
    if weights is None:
        weights = {sid: 1.0 / len(stock_ids) for sid in stock_ids}

    # 驗證權重
    total_weight = sum(weights.values())
    if not np.isclose(total_weight, 1.0):
        raise ValueError(f"權重總和必須為 1.0，目前為 {total_weight}")

    # 對齊所有股票的日期（取交集）
    common_dates = None
    for df in stocks_data.values():
        dates = set(df["date"])
        common_dates = dates if common_dates is None else common_dates & dates

    common_dates = sorted(common_dates)

    # 初始化投資組合狀態
    cash = initial_capital
    positions = {sid: {"shares": 0, "avg_price": 0.0} for sid in stock_ids}

    # 初始配置資金
    for sid in stock_ids:
        df = stocks_data[sid]
        first_row = df[df["date"] == common_dates[0]].iloc[0]

        allocated = initial_capital * weights[sid]
        price = first_row["close"]
        shares = int(allocated // price)

        if shares > 0:
            cost = shares * price
            cash -= cost
            positions[sid]["shares"] = shares
            positions[sid]["avg_price"] = price

    # 記錄每日持倉與權益
    daily_records = []
    all_trades = {sid: [] for sid in stock_ids}

    for date in common_dates:
        # 當日各股持倉市值
        holdings = {}
        for sid in stock_ids:
            df = stocks_data[sid]
            row = df[df["date"] == date].iloc[0]
            price = row["close"]
            signal = row.get("signal", 0)

            shares = positions[sid]["shares"]
            market_value = shares * price
            holdings[sid] = market_value

            # 處理訊號（簡化版：全買全賣）
            if signal == 1 and shares == 0:  # 買入
                available = cash * weights[sid]
                buy_shares = int(available // price)
                if buy_shares > 0:
                    cost = buy_shares * price
                    cash -= cost
                    positions[sid]["shares"] = buy_shares
                    positions[sid]["avg_price"] = price

                    all_trades[sid].append({
                        "date": date,
                        "action": "BUY",
                        "price": price,
                        "shares": buy_shares,
                        "amount": cost,
                    })

            elif signal == -1 and shares > 0:  # 賣出
                proceeds = shares * price
                pnl = proceeds - shares * positions[sid]["avg_price"]
                cash += proceeds

                all_trades[sid].append({
                    "date": date,
                    "action": "SELL",
                    "price": price,
                    "shares": shares,
                    "amount": proceeds,
                    "pnl": pnl,
                })

                positions[sid]["shares"] = 0
                positions[sid]["avg_price"] = 0.0

        # 總權益 = 現金 + 所有持倉市值
        total_equity = cash + sum(holdings.values())

        daily_records.append({
            "date": date,
            "cash": cash,
            "total_equity": total_equity,
            **{f"{sid}_value": holdings[sid] for sid in stock_ids},
        })

    # 轉換為 DataFrame
    equity_curve = pd.DataFrame(daily_records)

    # 計算績效統計
    final_equity = equity_curve["total_equity"].iloc[-1]
    total_return = (final_equity - initial_capital) / initial_capital

    n_days = (equity_curve["date"].iloc[-1] - equity_curve["date"].iloc[0]).days
    years = max(n_days / 365.25, 1 / 365.25)
    annual_return = (1 + total_return) ** (1 / years) - 1

    daily_returns = equity_curve["total_equity"].pct_change().dropna()
    sharpe_ratio = 0.0
    if len(daily_returns) > 1 and daily_returns.std() > 0:
        excess = daily_returns.mean() - 0.015 / 252
        sharpe_ratio = excess / daily_returns.std() * np.sqrt(252)

    rolling_max = equity_curve["total_equity"].cummax()
    drawdown = (equity_curve["total_equity"] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    stats = {
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "initial_capital": initial_capital,
        "final_equity": final_equity,
        "total_trades": sum(len(trades) for trades in all_trades.values()),
    }

    return PortfolioResult(
        equity_curve=equity_curve,
        trades=all_trades,
        stats=stats,
    )
