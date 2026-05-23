"""Historical volatility calculation."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

ANNUALIZATION = {"daily": 252, "weekly": 52, "monthly": 12}


def log_returns(prices: pd.Series) -> pd.Series:
    p = pd.to_numeric(prices, errors="coerce").dropna()
    p = p[p > 0]
    return np.log(p / p.shift(1)).dropna()


def annualized_volatility(prices: pd.Series, frequency: str = "daily") -> dict:
    if frequency not in ANNUALIZATION:
        raise ValueError(f"Unknown frequency {frequency!r}")
    rets = log_returns(prices)
    if len(rets) < 2:
        raise ValueError("Not enough price observations to compute volatility")
    std = float(rets.std(ddof=1))
    factor = math.sqrt(ANNUALIZATION[frequency])
    return {
        "log_returns": rets,
        "period_std": std,
        "annualization_factor": factor,
        "annualized_volatility": std * factor,
        "n_observations": int(len(rets)),
        "frequency": frequency,
    }
