"""Black-Scholes option pricing."""
from __future__ import annotations

import math
from dataclasses import dataclass
from scipy.stats import norm


@dataclass
class BSInputs:
    S0: float
    K: float
    r: float
    sigma: float
    T: float
    q: float = 0.0


@dataclass
class BSResult:
    call: float
    put: float
    d1: float
    d2: float


def black_scholes(inp: BSInputs) -> BSResult:
    if inp.T <= 0:
        raise ValueError("Time to maturity T must be > 0")
    if inp.sigma <= 0:
        raise ValueError("Volatility sigma must be > 0")
    if inp.S0 <= 0 or inp.K <= 0:
        raise ValueError("S0 and K must be > 0")
    S0, K, r, q, sigma, T = inp.S0, inp.K, inp.r, inp.q, inp.sigma, inp.T
    d1 = (math.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call = S0 * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    put = K * math.exp(-r * T) * norm.cdf(-d2) - S0 * math.exp(-q * T) * norm.cdf(-d1)
    return BSResult(call=call, put=put, d1=d1, d2=d2)
