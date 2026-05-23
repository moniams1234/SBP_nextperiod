"""Subsequent period IFRS 2 valuation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class EquitySubsequentInputs:
    grant_date_fv_per_option: float
    instruments_granted: int
    updated_forfeiture_rate: float
    vesting_period_years: float
    cumulative_service_years: float
    cumulative_expense_prior: float


def equity_subsequent(inp: EquitySubsequentInputs) -> dict:
    updated_vested = inp.instruments_granted * (1.0 - inp.updated_forfeiture_rate)
    updated_total_fv = updated_vested * inp.grant_date_fv_per_option
    progress = min(1.0, inp.cumulative_service_years / inp.vesting_period_years) if inp.vesting_period_years > 0 else 1.0
    cumulative_required = updated_total_fv * progress
    current_period_expense = cumulative_required - inp.cumulative_expense_prior
    return {
        "updated_expected_vested": updated_vested,
        "updated_total_fair_value": updated_total_fv,
        "service_progress": progress,
        "cumulative_expense_required": cumulative_required,
        "current_period_expense": current_period_expense,
        "equity_reserve_closing": cumulative_required,
    }


def equity_subsequent_entries(current_expense: float) -> List[Dict]:
    return [
        {"Account": "Employee benefit expense (P&L)", "Debit": current_expense, "Credit": 0.0,
         "Explanation": "Catch-up adjustment based on updated expected vested instruments."},
        {"Account": "Share-based payment reserve (Equity)", "Debit": 0.0, "Credit": current_expense,
         "Explanation": "Equity-settled award: grant-date FV not remeasured."},
    ]


@dataclass
class CashSubsequentInputs:
    current_fv_per_option: float
    instruments_outstanding: int
    updated_forfeiture_rate: float
    vesting_progress: float           # 0..1
    opening_liability: float
    cash_paid_during_period: float


def cash_subsequent(inp: CashSubsequentInputs) -> dict:
    expected_vested = inp.instruments_outstanding * (1.0 - inp.updated_forfeiture_rate)
    closing_liability = inp.current_fv_per_option * expected_vested * max(0.0, min(1.0, inp.vesting_progress))
    pnl_impact = closing_liability - inp.opening_liability + inp.cash_paid_during_period
    return {
        "expected_vested": expected_vested,
        "current_fv_per_option": inp.current_fv_per_option,
        "opening_liability": inp.opening_liability,
        "closing_liability": closing_liability,
        "cash_paid": inp.cash_paid_during_period,
        "pnl_impact": pnl_impact,
    }


def cash_subsequent_entries(result: dict) -> List[Dict]:
    entries: List[Dict] = []
    delta = result["closing_liability"] - result["opening_liability"]
    if delta >= 0:
        entries.append({"Account": "Employee benefit expense (P&L)", "Debit": delta, "Credit": 0.0,
                        "Explanation": "Increase in liability remeasured at reporting date."})
        entries.append({"Account": "Share-based payment liability", "Debit": 0.0, "Credit": delta,
                        "Explanation": "Cash-settled: liability remeasured each period through P&L."})
    else:
        amt = -delta
        entries.append({"Account": "Share-based payment liability", "Debit": amt, "Credit": 0.0,
                        "Explanation": "Liability decreased on remeasurement."})
        entries.append({"Account": "Employee benefit expense / gain from remeasurement (P&L)", "Debit": 0.0,
                        "Credit": amt, "Explanation": "Gain from remeasurement recognized in P&L."})
    if result["cash_paid"] > 0:
        entries.append({"Account": "Share-based payment liability", "Debit": result["cash_paid"], "Credit": 0.0,
                        "Explanation": "Settlement of liability in cash."})
        entries.append({"Account": "Cash / bank", "Debit": 0.0, "Credit": result["cash_paid"],
                        "Explanation": "Cash outflow on settlement."})
    return entries


@dataclass
class ChoiceSubsequentInputs:
    has_cash_obligation: bool
    opening_liability: float
    updated_cash_fv: float
    updated_equity_fv: float
    updated_expected_vested: float
    vesting_progress: float
    cash_paid: float


def choice_subsequent(inp: ChoiceSubsequentInputs) -> dict:
    progress = max(0.0, min(1.0, inp.vesting_progress))
    liability_component = inp.updated_cash_fv * inp.updated_expected_vested * progress if inp.has_cash_obligation else 0.0
    equity_component = max(0.0, inp.updated_equity_fv - inp.updated_cash_fv) * inp.updated_expected_vested * progress
    remeasurement = liability_component - inp.opening_liability + inp.cash_paid
    return {
        "liability_component": liability_component,
        "equity_component": equity_component,
        "current_period_expense": liability_component + equity_component - inp.opening_liability + inp.cash_paid,
        "remeasurement_gain_loss": remeasurement,
        "cash_paid": inp.cash_paid,
    }


def choice_subsequent_entries(result: dict) -> List[Dict]:
    entries: List[Dict] = []
    if result["liability_component"] - 0 > 0:
        entries.append({"Account": "Employee benefit expense (P&L)", "Debit": result["liability_component"], "Credit": 0.0,
                        "Explanation": "Liability component remeasured at reporting date."})
        entries.append({"Account": "Share-based payment liability", "Debit": 0.0, "Credit": result["liability_component"],
                        "Explanation": "Cash-settled component (compound instrument)."})
    if result["equity_component"] > 0:
        entries.append({"Account": "Employee benefit expense (P&L)", "Debit": result["equity_component"], "Credit": 0.0,
                        "Explanation": "Equity component (residual) recognized over vesting period."})
        entries.append({"Account": "Share-based payment reserve (Equity)", "Debit": 0.0, "Credit": result["equity_component"],
                        "Explanation": "Equity component not remeasured after grant date."})
    if result["cash_paid"] > 0:
        entries.append({"Account": "Share-based payment liability", "Debit": result["cash_paid"], "Credit": 0.0,
                        "Explanation": "Cash settlement of liability portion."})
        entries.append({"Account": "Cash / bank", "Debit": 0.0, "Credit": result["cash_paid"],
                        "Explanation": "Cash outflow."})
    return entries
