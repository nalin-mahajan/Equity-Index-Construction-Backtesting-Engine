# metrics.py — Performance and risk metrics computation

import pandas as pd
import numpy as np
from typing import Dict
from config import RISK_FREE_RATE


def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    total = (1 + returns).prod()
    n = len(returns)
    return total ** (periods_per_year / n) - 1


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    return returns.std() * np.sqrt(periods_per_year)


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE,
    periods_per_year: int = 252,
) -> float:
    daily_rf = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess = returns - daily_rf
    if excess.std() == 0:
        return np.nan
    return (excess.mean() / excess.std()) * np.sqrt(periods_per_year)


def sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE,
    periods_per_year: int = 252,
) -> float:
    daily_rf = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess = returns - daily_rf
    downside = excess[excess < 0].std()
    if downside == 0:
        return np.nan
    return (excess.mean() / downside) * np.sqrt(periods_per_year)


def max_drawdown(nav: pd.Series) -> float:
    rolling_max = nav.cummax()
    drawdowns = (nav - rolling_max) / rolling_max
    return drawdowns.min()


def drawdown_series(nav: pd.Series) -> pd.Series:
    rolling_max = nav.cummax()
    return (nav - rolling_max) / rolling_max


def calmar_ratio(returns: pd.Series, nav: pd.Series, periods_per_year: int = 252) -> float:
    ann_ret = annualized_return(returns, periods_per_year)
    mdd = abs(max_drawdown(nav))
    return ann_ret / mdd if mdd != 0 else np.nan


def tracking_error(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    aligned = portfolio_returns.align(benchmark_returns, join="inner")
    active = aligned[0] - aligned[1]
    return active.std() * np.sqrt(periods_per_year)


def information_ratio(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    aligned = portfolio_returns.align(benchmark_returns, join="inner")
    active = aligned[0] - aligned[1]
    te = active.std() * np.sqrt(periods_per_year)
    if te == 0:
        return np.nan
    ann_active = active.mean() * periods_per_year
    return ann_active / te


def beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    aligned = portfolio_returns.align(benchmark_returns, join="inner")
    cov = np.cov(aligned[0], aligned[1])
    return cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else np.nan


def alpha(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = RISK_FREE_RATE,
    periods_per_year: int = 252,
) -> float:
    b = beta(portfolio_returns, benchmark_returns)
    p_ann = annualized_return(portfolio_returns, periods_per_year)
    bm_ann = annualized_return(benchmark_returns, periods_per_year)
    return p_ann - (risk_free_rate + b * (bm_ann - risk_free_rate))


def compute_all_metrics(
    portfolio_nav: pd.Series,
    benchmark_nav: pd.Series,
) -> Dict[str, float]:
    p_ret = portfolio_nav.pct_change().dropna()
    b_ret = benchmark_nav.pct_change().dropna()

    return {
        "Annualized Return":     round(annualized_return(p_ret) * 100, 2),
        "Annualized Volatility": round(annualized_volatility(p_ret) * 100, 2),
        "Sharpe Ratio":          round(sharpe_ratio(p_ret), 3),
        "Sortino Ratio":         round(sortino_ratio(p_ret), 3),
        "Max Drawdown (%)":      round(max_drawdown(portfolio_nav) * 100, 2),
        "Calmar Ratio":          round(calmar_ratio(p_ret, portfolio_nav), 3),
        "Tracking Error (%)":    round(tracking_error(p_ret, b_ret) * 100, 2),
        "Information Ratio":     round(information_ratio(p_ret, b_ret), 3),
        "Beta":                  round(beta(p_ret, b_ret), 3),
        "Alpha (%)":             round(alpha(p_ret, b_ret) * 100, 2),
        "Benchmark Ann. Return": round(annualized_return(b_ret) * 100, 2),
    }