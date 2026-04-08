# index_constructor.py — Build and rebalance the index

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from screener import apply_sector_cap
from config import INDEX_CONFIG, SCREENING_CRITERIA


def compute_weights(
    screened_df: pd.DataFrame,
    scheme: str = "equal",
    max_constituents: int = 50,
) -> pd.Series:
    """
    Compute constituent weights based on the chosen scheme.
    Scheme options: 'equal', 'market_cap'
    """
    df = screened_df.copy()

    # Sort by market cap descending, take top N
    df = df.sort_values("market_cap", ascending=False).head(max_constituents)

    if scheme == "equal":
        weights = pd.Series(1.0 / len(df), index=df.index)

    elif scheme == "market_cap":
        caps = df["market_cap"].fillna(0)
        weights = caps / caps.sum()

    else:
        raise ValueError(f"Unknown weighting scheme: {scheme}")

    # Apply sector cap if configured
    max_sw = SCREENING_CRITERIA.get("max_sector_weight", 1.0)
    if max_sw < 1.0 and "sector" in df.columns:
        sector_map = df["sector"]
        weights = apply_sector_cap(weights, sector_map, max_sw)

    weights = weights / weights.sum()   # ensure exact normalization
    return weights


def get_rebalance_dates(
    price_index: pd.DatetimeIndex,
    frequency: str = "Q",
) -> List[pd.Timestamp]:
    """
    Return a list of rebalance dates aligned to quarter-end (or other freq).
    Uses the first trading day after each period end.
    """
    period_ends = price_index.to_period(frequency).drop_duplicates()
    rebalance_dates = []
    for p in period_ends:
        period_end = p.to_timestamp("D", how="end")
        trading_days_after = price_index[price_index >= period_end]
        if len(trading_days_after) > 0:
            rebalance_dates.append(trading_days_after[0])
    return rebalance_dates


class IndexConstituentsHistory:
    """Stores the weights assigned at each rebalance date."""

    def __init__(self):
        self._history: Dict[pd.Timestamp, pd.Series] = {}

    def record(self, date: pd.Timestamp, weights: pd.Series):
        self._history[date] = weights

    def get_weights_at(self, date: pd.Timestamp) -> pd.Series:
        """Return the most recently set weights as of `date`."""
        past_dates = [d for d in self._history if d <= date]
        if not past_dates:
            return pd.Series(dtype=float)
        return self._history[max(past_dates)]

    def all_dates(self) -> List[pd.Timestamp]:
        return sorted(self._history.keys())

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self._history).T.fillna(0.0)