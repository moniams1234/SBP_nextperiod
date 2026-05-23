# Share-Based Payment Valuation App (IFRS 2)

Premium Streamlit toolkit to value and account for stock options, warrants,
and other share-based payment programs under IFRS 2.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tabs

1. **Program setup** — type (equity / cash / employee choice), instrument, dates, vesting, headcount, forfeiture.
2. **Black-Scholes** — d₁, d₂, N(d₁), N(d₂), call & put values, IFRS 2 selected FV.
3. **Volatility** — manual input or upload historical prices (daily/weekly/monthly). Handles Polish decimal commas.
4. **Vesting & forfeiture** — service / non-market performance conditions, expected vested instruments.
5. **First-year accounting** — total FV, annual & first-year expense, journal entries (incl. compound for choice).
6. **Subsequent period** — full IFRS 2 remeasurement logic per program type (see below).
7. **Summary & export** — executive KPI dashboard + multi-sheet Excel report.

## IFRS 2 background

**Black-Scholes**

```
d1 = [ln(S0/K) + (r − q + σ²/2) · T] / (σ · √T)
d2 = d1 − σ · √T
Call = S0 · e^(−qT) · N(d1) − K · e^(−rT) · N(d2)
Put  = K · e^(−rT) · N(−d2) − S0 · e^(−qT) · N(−d1)
```

**Volatility**

Log returns `ln(Pt / Pt-1)`, std dev annualized by √252 / √52 / √12.

**Equity-settled**: grant-date fair value is fixed and never remeasured.
Only the **expected number of vesting instruments** is updated each period
(non-market conditions, employee turnover). Expense is the catch-up between
required cumulative expense and what was already booked. DR P&L / CR Equity.

**Cash-settled**: the **liability** is remeasured at every reporting date at
current fair value (recompute Black-Scholes). DR/CR P&L for the movement,
plus DR liability / CR cash on settlement.

**Employee choice (compound)**: split into liability component (cash
alternative, remeasured) and equity component (residual, NOT remeasured).
Classification depends on whether the entity has a present obligation to
settle in cash — confirm with auditors.

**First-year expense**

```
Total FV = grant-date FV per option × expected vested instruments
Annual expense = Total FV / vesting period
First-year expense = Annual expense × months active / 12
```

**Subsequent period expense (equity-settled)**

```
Cumulative required = updated total FV × (service completed / vesting period)
Current period expense = Cumulative required − Cumulative recognized prior
```

## Disclaimer

This tool is for educational and analytical purposes only. Final IFRS 2
classification and accounting treatment should be reviewed based on the legal
terms of the share-based payment plan and confirmed with professional
accounting advisors or auditors.
