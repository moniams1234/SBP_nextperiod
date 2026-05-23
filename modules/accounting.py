"""IFRS 2 expense & accounting entries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ValuationInputs:
    program_type: str
    fair_value_per_option: float
    options_granted: int
    forfeiture_rate: float
    vesting_period_years: float
    months_in_first_year: int = 12
    has_liability: bool = False
    liability_value: float = 0.0
    cash_alternative_value: float = 0.0
    equity_alternative_value: float = 0.0


def compute_valuation(v: ValuationInputs) -> dict:
    expected_vested = v.options_granted * (1.0 - v.forfeiture_rate)
    total_fv = expected_vested * v.fair_value_per_option
    annual_expense = total_fv / v.vesting_period_years if v.vesting_period_years > 0 else total_fv
    months = max(0, min(12, int(v.months_in_first_year)))
    first_year_expense = annual_expense * months / 12.0

    result = {
        "expected_vested_options": expected_vested,
        "total_fair_value": total_fv,
        "annual_expense": annual_expense,
        "first_year_expense": first_year_expense,
        "liability_amount": 0.0,
        "equity_reserve_amount": 0.0,
    }

    if v.program_type == "equity":
        result["equity_reserve_amount"] = total_fv
    elif v.program_type == "cash":
        result["liability_amount"] = total_fv
    elif v.program_type == "choice":
        liability_component = v.liability_value if v.has_liability else v.cash_alternative_value
        equity_component = max(0.0, v.equity_alternative_value - liability_component)
        result["liability_amount"] = liability_component
        result["equity_reserve_amount"] = equity_component
        result["total_fair_value"] = liability_component + equity_component
        if v.vesting_period_years > 0:
            result["annual_expense"] = result["total_fair_value"] / v.vesting_period_years
        else:
            result["annual_expense"] = result["total_fair_value"]
        result["first_year_expense"] = result["annual_expense"] * months / 12.0
    return result


def accounting_entries(program_type: str, valuation: dict) -> List[Dict]:
    amount = valuation["first_year_expense"]
    entries: List[Dict] = []
    if program_type == "equity":
        entries.append({"Account": "Employee benefit expense (P&L)", "Debit": amount, "Credit": 0.0,
                        "Explanation": "Recognize expense over vesting period (grant-date FV, not remeasured)."})
        entries.append({"Account": "Share-based payment reserve (Equity)", "Debit": 0.0, "Credit": amount,
                        "Explanation": "Credit equity for equity-settled award."})
    elif program_type == "cash":
        entries.append({"Account": "Employee benefit expense (P&L)", "Debit": amount, "Credit": 0.0,
                        "Explanation": "Expense based on FV at reporting date x vesting progress."})
        entries.append({"Account": "Share-based payment liability", "Debit": 0.0, "Credit": amount,
                        "Explanation": "Liability remeasured at each reporting date through P&L."})
    elif program_type == "choice":
        total = valuation["total_fair_value"] or 1.0
        liab_share = valuation["liability_amount"] / total
        eq_share = valuation["equity_reserve_amount"] / total
        entries.append({"Account": "Employee benefit expense (P&L)", "Debit": amount, "Credit": 0.0,
                        "Explanation": "Compound instrument: expense recognized over vesting period."})
        entries.append({"Account": "Share-based payment liability", "Debit": 0.0, "Credit": amount * liab_share,
                        "Explanation": "Liability component (cash alternative), remeasured each period."})
        entries.append({"Account": "Share-based payment reserve (Equity)", "Debit": 0.0, "Credit": amount * eq_share,
                        "Explanation": "Equity component (residual), not remeasured after grant date."})
    return entries
