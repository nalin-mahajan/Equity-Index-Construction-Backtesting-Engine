# backtester.py — Simulate index performance with transaction costs

import pandas as pd
import numpy as np
from typing import Tuple
from config import BACKTEST_CONFIG
from index_constructor import IndexConstituentsHistory


def run_backtest(
    price_data: pd.DataFrame,
    constituents_history: IndexConstituentsHistory,
    initial_capital: float = 1_000_000,
    transaction_cost_bps: float = 10,
) -> Tuple[pd.Series, pd.DataFrame]:
    """
    Simulate daily portfolio returns using pre-computed rebalance weights.

    Returns:
        portfolio_value : daily portfolio NAV series
        holdings_df     : daily dollar holdings per ticker
    """
    tc_rate = transaction_cost_bps / 10_000

    # Align prices to available data
    prices = price_data.copy().ffill().dropna(how="all")
    daily_returns = prices.pct_change().fillna(0.0)

    portfolio_value = pd.Series(index=prices.index, dtype=float)
    holdings = pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)

    rebalance_dates = set(constituents_history.all_dates())
    current_weights = pd.Series(dtype=float)
    nav = initial_capital

    for i, date in enumerate(prices.index):
        # ---- Rebalance if needed ----
        if date in rebalance_dates:
            new_weights = constituents_history.get_weights_at(date)

            # Compute turnover vs previous weights
            if not current_weights.empty:
                all_tickers = new_weights.index.union(current_weights.index)
                old_w = current_weights.reindex(all_tickers).fillna(0)
                new_w = new_weights.reindex(all_tickers).fillna(0)
                turnover = (new_w - old_w).abs().sum() / 2
                tc_cost = turnover * tc_rate * nav
                nav -= tc_cost

            current_weights = new_weights

        # ---- Apply daily returns ----
        if not current_weights.empty and i > 0:
            available = current_weights.index.intersection(daily_returns.columns)
            day_ret = (current_weights[available] * daily_returns.loc[date, available]).sum()
            nav *= (1 + day_ret)

        portfolio_value.loc[date] = nav

        # Record dollar holdings
        if not current_weights.empty:
            dollar_holdings = current_weights.reindex(prices.columns).fillna(0) * nav
            holdings.loc[date] = dollar_holdings
        else:
            holdings.loc[date] = 0.0

    return portfolio_value, holdings


def compute_daily_returns(nav_series: pd.Series) -> pd.Series:
    return nav_series.pct_change().dropna()