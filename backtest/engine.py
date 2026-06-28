from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    trades: list = field(default_factory=list)
    equity_curve: pd.DataFrame = field(default_factory=pd.DataFrame)
    stats: dict = field(default_factory=dict)


def run_backtest(
    df: pd.DataFrame,
    signal_column: str = "signal",
    initial_capital: float = 1_000_000,
) -> BacktestResult:
    df = df.copy().reset_index(drop=True)

    cash = initial_capital
    shares = 0
    position_open = False
    entry_price = 0.0
    entry_date = None
    trades = []

    dates = []
    equity_values = []

    for i, row in df.iterrows():
        sig = row[signal_column]
        price = row["close"]
        date = row["date"]

        if sig == 1 and not position_open:
            shares = int(cash // price)
            if shares > 0:
                cost = shares * price
                cash -= cost
                position_open = True
                entry_price = price
                entry_date = date

        elif sig == -1 and position_open:
            proceeds = shares * price
            pnl = proceeds - shares * entry_price
            trades.append({
                "entry_date": entry_date,
                "exit_date": date,
                "entry_price": entry_price,
                "exit_price": price,
                "shares": shares,
                "pnl": pnl,
                "return_pct": (price - entry_price) / entry_price * 100,
            })
            cash += proceeds
            shares = 0
            position_open = False

        total_equity = cash + shares * price
        dates.append(date)
        equity_values.append(total_equity)

    if position_open:
        last_price = df.iloc[-1]["close"]
        last_date = df.iloc[-1]["date"]
        proceeds = shares * last_price
        pnl = proceeds - shares * entry_price
        trades.append({
            "entry_date": entry_date,
            "exit_date": last_date,
            "entry_price": entry_price,
            "exit_price": last_price,
            "shares": shares,
            "pnl": pnl,
            "return_pct": (last_price - entry_price) / entry_price * 100,
        })

    equity_curve = pd.DataFrame({
        "date": dates,
        "equity": equity_values,
        "close": df["close"].values,
    })
    stats = _compute_stats(equity_curve, trades, initial_capital)

    return BacktestResult(trades=trades, equity_curve=equity_curve, stats=stats)


def _compute_stats(
    equity_curve: pd.DataFrame,
    trades: list,
    initial_capital: float,
) -> dict:
    if equity_curve.empty:
        return {}

    final_equity = equity_curve["equity"].iloc[-1]
    total_return = (final_equity - initial_capital) / initial_capital

    n_days = (equity_curve["date"].iloc[-1] - equity_curve["date"].iloc[0]).days
    years = max(n_days / 365.25, 1 / 365.25)
    annual_return = (1 + total_return) ** (1 / years) - 1

    daily_returns = equity_curve["equity"].pct_change().dropna()
    sharpe_ratio = 0.0
    if len(daily_returns) > 1 and daily_returns.std() > 0:
        excess = daily_returns.mean() - 0.015 / 252
        sharpe_ratio = excess / daily_returns.std() * np.sqrt(252)

    rolling_max = equity_curve["equity"].cummax()
    drawdown = (equity_curve["equity"] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    winning = [t for t in trades if t["pnl"] > 0]
    losing = [t for t in trades if t["pnl"] <= 0]
    win_rate = len(winning) / len(trades) * 100 if trades else 0

    gross_profit = sum(t["pnl"] for t in winning) if winning else 0
    gross_loss = abs(sum(t["pnl"] for t in losing)) if losing else 0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "win_rate": win_rate,
        "total_trades": len(trades),
        "profit_factor": profit_factor,
        "initial_capital": initial_capital,
        "final_equity": final_equity,
    }
