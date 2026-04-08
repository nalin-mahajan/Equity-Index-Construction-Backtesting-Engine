# main.py — Orchestrates the full pipeline

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from config import INDEX_CONFIG, SCREENING_CRITERIA, BACKTEST_CONFIG
from data_loader import build_universe_df, fetch_price_data, get_benchmark_prices
from screener import apply_screens
from index_constructor import compute_weights, get_rebalance_dates, IndexConstituentsHistory
from backtester import run_backtest, compute_daily_returns
from metrics import compute_all_metrics
from report import plot_full_report


# ── 1. Define your candidate universe ────────────────────────────────────────
# In production you'd pull from an index provider or screener API.
# Here we use a representative S&P 500 subset as example.
CANDIDATE_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
    "AMD",  "INTC", "CRM",   "ADBE", "ORCL", "CSCO", "QCOM",
    "UNH",  "JNJ",  "LLY",   "ABBV", "MRK",  "PFE",  "TMO", "ABT",
    "HD",   "NKE",  "AMGN",  "GILD", "ISRG", "SYK",  "MDT",
    "JPM",  "BAC",  "WFC",   "GS",   "MS",   "BLK",  "AXP",
    "NFLX", "DIS",  "CMCSA", "T",    "VZ",
    "HON",  "BA",   "CAT",   "LMT",  "GE",   "MMM",  "RTX",
    "COST", "WMT",  "TGT",
]


def main():
    print("=" * 60)
    print("  Equity Index Construction & Backtesting Engine")
    print("=" * 60)

    start = BACKTEST_CONFIG["start_date"]
    end   = BACKTEST_CONFIG["end_date"]

    # ── 2. Fetch fundamentals & screen universe ───────────────────────────────
    print("\n[1/5] Building universe and applying screens...")
    universe_df = build_universe_df(CANDIDATE_UNIVERSE)
    screened_df = apply_screens(universe_df)

    if len(screened_df) < INDEX_CONFIG["min_constituents"]:
        raise ValueError(
            f"Only {len(screened_df)} stocks passed screening — need at least "
            f"{INDEX_CONFIG['min_constituents']}. Widen your criteria."
        )

    # ── 3. Fetch price history ────────────────────────────────────────────────
    print("[2/5] Fetching price history...")
    all_tickers   = screened_df.index.tolist()
    price_data    = fetch_price_data(all_tickers, start, end)
    benchmark_nav = get_benchmark_prices(BACKTEST_CONFIG["benchmark_ticker"], start, end)

    # Drop tickers with insufficient history (< 252 trading days)
    valid_tickers = price_data.columns[price_data.count() >= 252].tolist()
    price_data    = price_data[valid_tickers]
    screened_df   = screened_df.loc[screened_df.index.intersection(valid_tickers)]

    # ── 4. Compute weights at each rebalance date ─────────────────────────────
    print("[3/5] Computing index weights at each rebalance date...")
    rebalance_dates = get_rebalance_dates(price_data.index, INDEX_CONFIG["rebalance_frequency"])
    history = IndexConstituentsHistory()

    for date in rebalance_dates:
        # Use data available up to this rebalance date (point-in-time)
        current_screened = screened_df.copy()
        # In a real system you'd re-screen with point-in-time fundamentals here
        weights = compute_weights(
            current_screened,
            scheme=INDEX_CONFIG["weighting_scheme"],
            max_constituents=INDEX_CONFIG["max_constituents"],
        )
        # Only keep tickers with price data available
        valid_at_date = price_data.loc[:date].dropna(axis=1, how="all").columns
        weights = weights[weights.index.intersection(valid_at_date)]
        weights = weights / weights.sum()
        history.record(date, weights)

    print(f"   Rebalanced on {len(rebalance_dates)} dates")

    # ── 5. Run backtest ───────────────────────────────────────────────────────
    print("[4/5] Running backtest simulation...")
    portfolio_nav, holdings_df = run_backtest(
        price_data=price_data,
        constituents_history=history,
        initial_capital=BACKTEST_CONFIG["initial_capital"],
        transaction_cost_bps=BACKTEST_CONFIG["transaction_cost_bps"],
    )

    # Align benchmark to portfolio dates
    benchmark_aligned = benchmark_nav.reindex(portfolio_nav.index, method="ffill")
    benchmark_aligned = benchmark_aligned * (
        BACKTEST_CONFIG["initial_capital"] / benchmark_aligned.iloc[0]
    )

    # ── 6. Compute metrics & report ───────────────────────────────────────────
    print("[5/5] Computing metrics and generating report...\n")
    metrics = compute_all_metrics(portfolio_nav, benchmark_aligned)

    print("─" * 40)
    print(f"{'Metric':<28} {'Value':>10}")
    print("─" * 40)
    for k, v in metrics.items():
        unit = "%" if "%" in k or "Return" in k or "Volatility" in k else ""
        print(f"{k:<28} {v:>10}{unit}")
    print("─" * 40)

    plot_full_report(
        portfolio_nav,
        benchmark_aligned,
        metrics,
        constituents_history=history,
        title=f"{INDEX_CONFIG['name']} vs {BACKTEST_CONFIG['benchmark_ticker']}",
    )

    # ── Optional: export constituent weight history ───────────────────────────
    weight_df = history.to_dataframe()
    weight_df.to_csv("constituent_weights.csv")
    print("\nConstituent weights saved to constituent_weights.csv")


if __name__ == "__main__":
    main()