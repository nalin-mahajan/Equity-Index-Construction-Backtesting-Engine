# report.py — Visualise backtest results using matplotlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import Dict
from metrics import drawdown_series


STYLE = {
    "portfolio_color": "#2563EB",
    "benchmark_color": "#64748B",
    "drawdown_color":  "#EF4444",
    "figsize": (16, 12),
}


def plot_full_report(
    portfolio_nav: pd.Series,
    benchmark_nav: pd.Series,
    metrics: Dict[str, float],
    constituents_history=None,
    title: str = "Custom Index Backtest Report",
):
    fig = plt.figure(figsize=STYLE["figsize"])
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    ax4 = fig.add_subplot(gs[2, 0])
    ax5 = fig.add_subplot(gs[2, 1])

    # ---- 1. Cumulative NAV ----
    port_norm  = portfolio_nav  / portfolio_nav.iloc[0] * 100
    bench_norm = benchmark_nav  / benchmark_nav.iloc[0] * 100
    ax1.plot(port_norm,  label="Custom Index", color=STYLE["portfolio_color"], lw=1.8)
    ax1.plot(bench_norm, label="Benchmark",    color=STYLE["benchmark_color"], lw=1.4, ls="--")
    ax1.set_title("Cumulative Performance (rebased to 100)")
    ax1.legend(frameon=False)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel("NAV (indexed)")

    # ---- 2. Drawdown ----
    dd = drawdown_series(portfolio_nav) * 100
    ax2.fill_between(dd.index, dd, 0, color=STYLE["drawdown_color"], alpha=0.5)
    ax2.plot(dd, color=STYLE["drawdown_color"], lw=0.8)
    ax2.set_title("Portfolio Drawdown (%)")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel("%")

    # ---- 3. Rolling Sharpe (1Y) ----
    p_ret = portfolio_nav.pct_change().dropna()
    rolling_sharpe = p_ret.rolling(252).apply(
        lambda x: (x.mean() / x.std() * np.sqrt(252)) if x.std() > 0 else np.nan
    )
    ax3.plot(rolling_sharpe, color=STYLE["portfolio_color"], lw=1.2)
    ax3.axhline(0, color="gray", lw=0.8, ls="--")
    ax3.set_title("Rolling 1Y Sharpe Ratio")
    ax3.grid(True, alpha=0.3)

    # ---- 4. Annual Returns Bar Chart ----
    annual_p  = port_norm.resample("YE").last().pct_change().dropna() * 100
    annual_b  = bench_norm.resample("YE").last().pct_change().dropna() * 100
    years = annual_p.index.year
    x = np.arange(len(years))
    w = 0.35
    ax4.bar(x - w/2, annual_p.values, w, label="Index",     color=STYLE["portfolio_color"], alpha=0.85)
    ax4.bar(x + w/2, annual_b.values, w, label="Benchmark", color=STYLE["benchmark_color"], alpha=0.85)
    ax4.set_xticks(x)
    ax4.set_xticklabels(years, rotation=45)
    ax4.axhline(0, color="black", lw=0.7)
    ax4.set_title("Annual Returns (%)")
    ax4.legend(frameon=False, fontsize=8)
    ax4.grid(True, alpha=0.3, axis="y")

    # ---- 5. Metrics Table ----
    ax5.axis("off")
    rows = list(metrics.items())
    table = ax5.table(
        cellText=[[k, f"{v:>10}"] for k, v in rows],
        colLabels=["Metric", "Value"],
        cellLoc="left",
        loc="center",
        colWidths=[0.65, 0.35],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)
    ax5.set_title("Performance Summary", pad=12)

    plt.savefig("backtest_report.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Report saved to backtest_report.png")