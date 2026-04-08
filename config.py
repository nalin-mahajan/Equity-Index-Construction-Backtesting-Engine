# config.py — Central configuration for the index engine

INDEX_CONFIG = {
    "name": "Custom Equal-Weight Index",
    "rebalance_frequency": "Q",          # Q = quarterly
    "weighting_scheme": "equal",         # Options: 'equal', 'market_cap'
    "max_constituents": 50,
    "min_constituents": 10,
}

SCREENING_CRITERIA = {
    "min_market_cap_usd": 2e9,           # $2B minimum (mid-cap+)
    "min_avg_daily_volume_usd": 5e6,     # $5M average daily volume
    "min_price": 5.0,                    # Exclude penny stocks
    "allowed_sectors": [                  # None = allow all
        "Technology",
        "Health Care",
        "Consumer Discretionary",
        "Industrials",
        "Financials",
        "Communication Services",
    ],
    "max_sector_weight": 0.30,           # 30% sector cap
    "exclude_reits": True,
    "exclude_adrs": False,
}

BACKTEST_CONFIG = {
    "start_date": "2018-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 1_000_000,
    "transaction_cost_bps": 10,          # 10 basis points per trade
    "benchmark_ticker": "SPY",
}

RISK_FREE_RATE = 0.04   # Annual, for Sharpe ratio calculation