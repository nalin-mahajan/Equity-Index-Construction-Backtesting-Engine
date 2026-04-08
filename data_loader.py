# data_loader.py — Fetch price, fundamentals, and metadata via yfinance

import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional
import warnings
warnings.filterwarnings("ignore")


def fetch_price_data(
    tickers: List[str],
    start_date: str,
    end_date: str,
    price_col: str = "Adj Close",
) -> pd.DataFrame:
    """Download adjusted close prices for a list of tickers."""
    raw = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]]
        prices.columns = tickers
    prices.dropna(how="all", inplace=True)
    return prices


def fetch_stock_info(ticker: str) -> dict:
    """Return a dict of fundamental fields for a single ticker."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", np.nan),
            "avg_daily_volume": info.get("averageDailyVolume10Day", np.nan),
            "price": info.get("regularMarketPrice", np.nan),
            "country": info.get("country", "Unknown"),
            "quote_type": info.get("quoteType", "Unknown"),
        }
    except Exception:
        return {"ticker": ticker, "sector": "Unknown", "market_cap": np.nan,
                "avg_daily_volume": np.nan, "price": np.nan, "quote_type": "Unknown"}


def build_universe_df(tickers: List[str]) -> pd.DataFrame:
    """Fetch fundamental info for all tickers and return as DataFrame."""
    records = [fetch_stock_info(t) for t in tickers]
    return pd.DataFrame(records).set_index("ticker")


def get_benchmark_prices(ticker: str, start_date: str, end_date: str) -> pd.Series:
    """Return benchmark price series (e.g. SPY)."""
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, progress=False)
    return df["Close"].squeeze()