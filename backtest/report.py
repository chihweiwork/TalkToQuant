import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def generate_report(
    result,
    benchmark_df: pd.DataFrame,
    strategy_name: str,
    stock_id: str,
    date_range: tuple,
) -> tuple:
    summary = _build_summary(result, benchmark_df, strategy_name, stock_id, date_range)
    html_path = _build_chart(result, benchmark_df, strategy_name, stock_id, date_range)

    # 產生 Tailscale HTTP URL
    import subprocess
    try:
        tailscale_ip = subprocess.check_output(
            ["tailscale", "ip", "-4"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        tailscale_ip = "100.95.111.123"  # Fallback to default

    # 取得相對路徑
    project_root = os.path.dirname(os.path.dirname(__file__))
    relative_path = os.path.relpath(html_path, project_root)
    http_url = f"http://{tailscale_ip}:8888/{relative_path}"

    return summary, html_path, http_url


def _build_summary(result, benchmark_df, strategy_name, stock_id, date_range) -> str:
    stats = result.stats
    start, end = date_range

    total_ret = stats["total_return"] * 100
    annual_ret = stats["annual_return"] * 100
    max_dd = stats["max_drawdown"] * 100
    sharpe = stats["sharpe_ratio"]
    win_rate = stats["win_rate"]
    n_trades = stats["total_trades"]
    profit_factor = stats["profit_factor"]

    if not benchmark_df.empty:
        bm_start = benchmark_df["price"].iloc[0]
        bm_end = benchmark_df["price"].iloc[-1]
        bm_return = (bm_end - bm_start) / bm_start * 100
    else:
        bm_return = 0.0

    alpha = total_ret - bm_return

    if alpha > 0:
        verdict = f"🔥 恭喜！此策略在測試期間「擊敗了市場」，帶來了 {alpha:.2f}% 的超額報酬！"
    elif alpha == 0:
        verdict = "📊 此策略表現與大盤持平。"
    else:
        verdict = f"📉 此策略在測試期間「落後大盤」{abs(alpha):.2f}%，可考慮調整參數。"

    pf_str = f"{profit_factor:.2f}" if profit_factor != float("inf") else "∞"

    lines = [
        "",
        "🤖 AI 策略研究員報告：",
        "=" * 50,
        f"📊 策略名稱：{strategy_name}",
        f"📅 測試區間：{start} ~ {end}",
        "=" * 50,
        "",
        "📈 回測結果摘要：",
        f"   - 您的 AI 策略總報酬率：{total_ret:+.2f}%",
        f"   - 期間大盤（買入持有）報酬率：{bm_return:+.2f}%",
        f"   {verdict}",
        "",
        "📋 詳細統計：",
        f"   - 年化報酬率：{annual_ret:+.2f}%",
        f"   - 最大回撤：{max_dd:.2f}%",
        f"   - Sharpe Ratio：{sharpe:.2f}",
        f"   - 勝率：{win_rate:.1f}%",
        f"   - 總交易次數：{n_trades}",
        f"   - 獲利因子：{pf_str}",
        "",
    ]
    return "\n".join(lines)


def _build_chart(result, benchmark_df, strategy_name, stock_id, date_range) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)

    eq = result.equity_curve.copy()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("資產曲線 vs 大盤", "買賣訊號"),
        row_heights=[0.6, 0.4],
    )

    eq_norm = eq["equity"] / eq["equity"].iloc[0] * 100
    fig.add_trace(
        go.Scatter(
            x=eq["date"], y=eq_norm,
            name="策略淨值",
            line=dict(color="#2196F3", width=2),
        ),
        row=1, col=1,
    )

    if not benchmark_df.empty:
        bm = benchmark_df.copy()
        bm_norm = bm["price"] / bm["price"].iloc[0] * 100
        fig.add_trace(
            go.Scatter(
                x=bm["date"], y=bm_norm,
                name="大盤（TAIEX）",
                line=dict(color="#FF9800", width=2, dash="dot"),
            ),
            row=1, col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=eq["date"], y=eq["equity"],
            name="資產總值 (TWD)",
            line=dict(color="#4CAF50", width=1.5),
            visible="legendonly",
        ),
        row=1, col=1,
    )

    buy_trades = [t for t in result.trades]
    if buy_trades:
        buy_dates = [t["entry_date"] for t in buy_trades]
        buy_prices = [t["entry_price"] for t in buy_trades]
        sell_dates = [t["exit_date"] for t in buy_trades]
        sell_prices = [t["exit_price"] for t in buy_trades]

        fig.add_trace(
            go.Scatter(
                x=buy_dates, y=buy_prices,
                mode="markers",
                name="買進",
                marker=dict(color="#4CAF50", size=10, symbol="triangle-up"),
            ),
            row=2, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=sell_dates, y=sell_prices,
                mode="markers",
                name="賣出",
                marker=dict(color="#F44336", size=10, symbol="triangle-down"),
            ),
            row=2, col=1,
        )

    if hasattr(result, "equity_curve") and "close" not in eq.columns:
        pass
    else:
        if "close" in eq.columns:
            fig.add_trace(
                go.Scatter(
                    x=eq["date"], y=eq["close"],
                    name="收盤價",
                    line=dict(color="#9E9E9E", width=1),
                ),
                row=2, col=1,
            )

    fig.update_layout(
        title=dict(text=f"📊 {strategy_name}", font=dict(size=18)),
        template="plotly_white",
        height=700,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(title_text="淨值（基準=100）", row=1, col=1)
    fig.update_yaxes(title_text="股價 (TWD)", row=2, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backtest_{stock_id}_{timestamp}.html"
    filepath = os.path.join(REPORTS_DIR, filename)

    # 使用 CDN 而非嵌入完整 Plotly.js，大幅減小檔案體積（4.7MB → ~100KB）
    fig.write_html(
        filepath,
        include_plotlyjs='cdn',
        config={
            'displayModeBar': True,
            'responsive': True,
            'displaylogo': False,
        }
    )

    return os.path.abspath(filepath)
