# screener.py — Apply rule-based screening to filter the investment universe

import pandas as pd
from typing import List, Optional
from config import SCREENING_CRITERIA


def apply_screens(universe_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all configured screening criteria to universe_df.
    Returns filtered DataFrame of passing stocks.
    """
    criteria = SCREENING_CRITERIA
    df = universe_df.copy()
    initial_count = len(df)

    # --- Market cap filter ---
    df = df[df["market_cap"] >= criteria["min_market_cap_usd"]]
    print(f"After market cap filter:      {len(df):>4} stocks (removed {initial_count - len(df)})")

    # --- Liquidity filter ---
    pre = len(df)
    df = df[df["avg_daily_volume"] >= criteria["min_avg_daily_volume_usd"]]
    print(f"After liquidity filter:       {len(df):>4} stocks (removed {pre - len(df)})")

    # --- Price filter ---
    pre = len(df)
    df = df[df["price"] >= criteria["min_price"]]
    print(f"After price filter:           {len(df):>4} stocks (removed {pre - len(df)})")

    # --- Sector filter ---
    if criteria.get("allowed_sectors"):
        pre = len(df)
        df = df[df["sector"].isin(criteria["allowed_sectors"])]
        print(f"After sector filter:          {len(df):>4} stocks (removed {pre - len(df)})")

    # --- Exclude REITs ---
    if criteria.get("exclude_reits"):
        pre = len(df)
        df = df[~df["industry"].str.contains("REIT|Real Estate Investment", case=False, na=False)]
        print(f"After REIT exclusion:         {len(df):>4} stocks (removed {pre - len(df)})")

    # --- Exclude ADRs (non-US) ---
    if not criteria.get("exclude_adrs", False):
        pass  # keep all
    else:
        pre = len(df)
        df = df[df["quote_type"] != "DEPOSITARY_RECEIPT"]
        print(f"After ADR exclusion:          {len(df):>4} stocks (removed {pre - len(df)})")

    print(f"\nFinal screened universe:      {len(df):>4} stocks\n")
    return df


def apply_sector_cap(
    weights: pd.Series,
    sector_map: pd.Series,
    max_sector_weight: float = 0.30,
) -> pd.Series:
    """
    Iteratively redistribute weight from over-weighted sectors.
    Returns normalized weights respecting the sector cap.
    """
    weights = weights.copy()
    for _ in range(20):                   # iterate until convergence
        sector_weights = weights.groupby(sector_map).sum()
        over = sector_weights[sector_weights > max_sector_weight]
        if over.empty:
            break
        for sector, sw in over.items():
            excess = sw - max_sector_weight
            in_sector = weights[sector_map == sector]
            # trim proportionally
            trim = in_sector / in_sector.sum() * excess
            weights[sector_map == sector] -= trim
            # redistribute to other sectors evenly
            outside = weights.index[sector_map != sector]
            weights[outside] += excess / len(outside)
        weights = weights.clip(lower=0)
        weights /= weights.sum()
    return weights