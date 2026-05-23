"""Share-Based Payment Valuation App (IFRS 2) - Streamlit."""
from __future__ import annotations

import datetime as dt
import pandas as pd
import streamlit as st

from modules.styling import inject_css, hero, disclaimer, kpi_grid, fmt_money, fmt_pct
from modules.black_scholes import BSInputs, black_scholes
from modules.volatility import annualized_volatility, log_returns
from modules.accounting import ValuationInputs, compute_valuation, accounting_entries
from modules.subsequent_valuation import (
    EquitySubsequentInputs, equity_subsequent, equity_subsequent_entries,
    CashSubsequentInputs, cash_subsequent, cash_subsequent_entries,
    ChoiceSubsequentInputs, choice_subsequent, choice_subsequent_entries,
)
from modules.utils import parse_number, coerce_numeric_series, read_uploaded_table
from modules.export_excel import build_excel


# ---------------- Page config ----------------
st.set_page_config(page_title="Share-Based Payment Valuation App",
                   page_icon="📈", layout="wide", initial_sidebar_state="expanded")
inject_css()

# ---------------- Session defaults ----------------
ss = st.session_state
ss.setdefault("program", {})
ss.setdefault("bs", {})
ss.setdefault("vol", {})
ss.setdefault("vesting", {})
ss.setdefault("first_year", {})
ss.setdefault("subsequent", {})
ss.setdefault("historical_prices", None)
ss.setdefault("log_returns", None)

PROGRAM_TYPES = {
    "Equity-settled": "equity",
    "Cash-settled": "cash",
    "Employee choice (cash or equity)": "choice",
}

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### 📈 SBP Valuation")
    st.caption("IFRS 2 toolkit")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.markdown(
        "- Program setup\n- Black-Scholes\n- Volatility\n- Vesting & forfeiture\n"
        "- First-year accounting\n- Subsequent period\n- Summary & export"
    )
    st.markdown("---")
    st.caption("Educational tool. Confirm IFRS 2 treatment with your auditors.")

# ---------------- Header ----------------
hero("Share-Based Payment Valuation App",
     "Premium IFRS 2 toolkit · Black-Scholes valuation, vesting accounting, subsequent remeasurement")
disclaimer()

tabs = st.tabs([
    "1 · Program setup",
    "2 · Black-Scholes",
    "3 · Volatility",
    "4 · Vesting & forfeiture",
    "5 · First-year accounting",
    "6 · Subsequent period",
    "7 · Summary & export",
])

# ============================================================
# TAB 1 — Program setup
# ============================================================
with tabs[0]:
    st.subheader("Program setup")
    c1, c2, c3 = st.columns(3)
    with c1:
        program_label = st.selectbox("Program type", list(PROGRAM_TYPES.keys()), key="setup_program_type")
        instrument_type = st.selectbox("Instrument type",
                                       ["Stock option", "Warrant", "RSU / Performance share"], key="setup_instrument_type")
        grant_date = st.date_input("Grant date", value=dt.date.today(), key="setup_grant_date")
    with c2:
        reporting_date = st.date_input("Reporting date", value=dt.date.today(), key="setup_reporting_date")
        program_start = st.date_input("Program start date", value=dt.date.today(), key="setup_program_start")
        vesting_period = st.number_input("Vesting period (years)", min_value=0.0, value=3.0, step=0.5, key="setup_vesting_period")
    with c3:
        expected_life = st.number_input("Total expected life (years)", min_value=0.0, value=5.0, step=0.5, key="setup_expected_life")
        n_employees = st.number_input("Number of employees", min_value=0, value=50, step=1, key="setup_n_employees")
        per_employee = st.number_input("Options / warrants per employee", min_value=0, value=1000, step=100, key="setup_per_employee")

    c4, c5, c6 = st.columns(3)
    with c4:
        total_granted = st.number_input("Total instruments granted",
                                        min_value=0, value=int(n_employees * per_employee), step=100, key="setup_total_granted")
    with c5:
        forfeiture_rate_pct = st.number_input("Expected forfeiture / turnover rate (%)",
                                              min_value=0.0, max_value=100.0, value=10.0, step=0.5, key="setup_forfeiture_rate_pct")
    with c6:
        expected_vest_pct = st.number_input("Expected % vesting (override)",
                                            min_value=0.0, max_value=100.0,
                                            value=100.0 - forfeiture_rate_pct, step=0.5, key="setup_expected_vest_pct")

    forfeiture_rate = 1.0 - expected_vest_pct / 100.0
    expected_vested = total_granted * (1.0 - forfeiture_rate)

    ss.program = dict(
        program_type=PROGRAM_TYPES[program_label], program_label=program_label,
        instrument_type=instrument_type,
        grant_date=str(grant_date), reporting_date=str(reporting_date),
        program_start=str(program_start),
        vesting_period_years=float(vesting_period), expected_life_years=float(expected_life),
        n_employees=int(n_employees), per_employee=int(per_employee),
        total_granted=int(total_granted), forfeiture_rate=float(forfeiture_rate),
        expected_vested=float(expected_vested),
    )

    st.markdown("---")
    kpi_grid([
        ("Program type", program_label, instrument_type),
        ("Total instruments", fmt_money(total_granted, 0), "Granted at grant date"),
        ("Forfeiture rate", fmt_pct(forfeiture_rate, 2), "Updated expectation"),
        ("Expected vested", fmt_money(expected_vested, 0), "= granted × (1 − forfeit)"),
    ])

# ============================================================
# TAB 2 — Black-Scholes
# ============================================================
with tabs[1]:
    st.subheader("Black-Scholes valuation")
    c1, c2, c3 = st.columns(3)
    with c1:
        S0 = st.number_input("Current share price S₀", min_value=0.0001, value=100.0, step=1.0, format="%.4f", key="bs_S0")
        K  = st.number_input("Strike price K",        min_value=0.0001, value=100.0, step=1.0, format="%.4f", key="bs_K")
    with c2:
        r_pct = st.number_input("Risk-free rate r (%)", value=5.0, step=0.25, key="bs_r_pct")
        q_pct = st.number_input("Dividend yield q (%)", value=0.0, step=0.25, key="bs_q_pct")
    with c3:
        T = st.number_input("Time to maturity T (years)", min_value=0.0001,
                            value=float(ss.program.get("expected_life_years", 5.0)), step=0.25, key="bs_T")
        opt_type = st.selectbox("Option type used for IFRS 2", ["Call", "Put"], key="bs_option_type")

    sigma_default = float(ss.vol.get("annualized_volatility", 0.30))
    sigma_pct = st.number_input("Volatility σ (%) — auto from Tab 3 if computed",
                                min_value=0.01, value=sigma_default * 100.0, step=1.0, key="bs_sigma_pct")

    if st.button("Compute Black-Scholes", key="btn_compute_bs"):
        try:
            res = black_scholes(BSInputs(S0=S0, K=K, r=r_pct/100, sigma=sigma_pct/100,
                                         T=T, q=q_pct/100))
            from scipy.stats import norm
            ss.bs = dict(
                S0=S0, K=K, r=r_pct/100, q=q_pct/100, sigma=sigma_pct/100, T=T,
                d1=res.d1, d2=res.d2, Nd1=float(norm.cdf(res.d1)), Nd2=float(norm.cdf(res.d2)),
                call=res.call, put=res.put,
                selected_fv=res.call if opt_type == "Call" else res.put,
                option_type=opt_type,
            )
            st.success("Computed.")
        except Exception as e:
            st.error(f"Error: {e}")

    if ss.bs:
        b = ss.bs
        kpi_grid([
            ("d₁", fmt_money(b["d1"], 4), f"N(d₁) = {fmt_money(b['Nd1'], 4)}"),
            ("d₂", fmt_money(b["d2"], 4), f"N(d₂) = {fmt_money(b['Nd2'], 4)}"),
            ("Call value", fmt_money(b["call"], 4), "Per option"),
            ("Put value", fmt_money(b["put"], 4), "Per option"),
            ("Selected FV (IFRS 2)", fmt_money(b["selected_fv"], 4), b["option_type"]),
        ])

# ============================================================
# TAB 3 — Volatility
# ============================================================
with tabs[2]:
    st.subheader("Volatility calculation")
    method = st.radio("Method", ["Manual input", "Upload historical prices"], horizontal=True, key="vol_method")

    if method == "Manual input":
        man = st.number_input("Annual volatility (%)", min_value=0.0, value=30.0, step=1.0, key="vol_manual_pct")
        ss.vol = {"annualized_volatility": man / 100.0, "method": "manual"}
        st.info(f"Volatility set to {fmt_pct(man/100, 2)}")
    else:
        up = st.file_uploader("Upload CSV / XLSX", type=["csv", "xlsx", "xls"], key="vol_file_uploader")
        if up is not None:
            try:
                df = read_uploaded_table(up)
                ss.historical_prices = df
                st.dataframe(df.head(20), use_container_width=True)
                cols = list(df.columns)
                c1, c2 = st.columns(2)
                with c1:
                    by_name = st.selectbox("Price column (by name)", cols, key="vol_price_column_name")
                with c2:
                    by_idx = st.number_input("…or column number (1-based, 0 = ignore)",
                                             min_value=0, max_value=len(cols), value=0, key="vol_price_column_idx")
                freq = st.selectbox("Frequency", ["daily", "weekly", "monthly"], key="vol_frequency")
                if st.button("Compute volatility", key="btn_compute_vol"):
                    col = cols[by_idx - 1] if by_idx > 0 else by_name
                    series = coerce_numeric_series(df[col])
                    info = annualized_volatility(series, frequency=freq)
                    ss.vol = {
                        "method": "upload", "frequency": freq, "column": col,
                        "n_observations": info["n_observations"],
                        "period_std": info["period_std"],
                        "annualization_factor": info["annualization_factor"],
                        "annualized_volatility": info["annualized_volatility"],
                    }
                    ss.log_returns = info["log_returns"]
                    st.success(f"Annualized volatility: {fmt_pct(info['annualized_volatility'], 2)}")
            except Exception as e:
                st.error(f"Error: {e}")

    if ss.vol:
        kpi_grid([
            ("Annualized σ", fmt_pct(ss.vol["annualized_volatility"], 2), ss.vol.get("method", "")),
            ("Method", ss.vol.get("method", "manual"), ss.vol.get("frequency", "—")),
        ])

# ============================================================
# TAB 4 — Vesting & forfeiture
# ============================================================
with tabs[3]:
    st.subheader("Vesting & forfeiture assumptions")
    p = ss.program
    c1, c2, c3 = st.columns(3)
    with c1:
        n_emp = st.number_input("Employees at grant date", min_value=0,
                                value=int(p.get("n_employees", 50)), key="vesting_n_emp")
        turnover_pct = st.number_input("Expected employee turnover (%)",
                                       min_value=0.0, max_value=100.0, value=10.0, step=0.5, key="vesting_turnover_pct")
    with c2:
        forfeit_pct = st.number_input("Expected forfeiture rate (%)",
                                      min_value=0.0, max_value=100.0,
                                      value=float(p.get("forfeiture_rate", 0.1)) * 100, step=0.5, key="vesting_forfeit_pct")
        expected_leavers = int(n_emp * turnover_pct / 100)
        st.metric("Expected employees leaving before vesting", expected_leavers)
    with c3:
        vesting_yrs = st.number_input("Vesting period (years)", min_value=0.0,
                                      value=float(p.get("vesting_period_years", 3.0)), step=0.5, key="vesting_vesting_yrs")
        service_ok = st.selectbox("Service condition fulfilled?", ["Yes", "No"], key="vesting_service_ok")
        perf_ok = st.selectbox("Non-market performance condition fulfilled?", ["Yes", "No"], key="vesting_perf_ok")

    expected_vest_pct = st.slider("Expected % of instruments vesting", 0.0, 100.0,
                                  float(100.0 - forfeit_pct), step=0.5, key="vesting_expected_vest_pct_slider")

    granted = int(p.get("total_granted", 0))
    expected_vested = granted * expected_vest_pct / 100.0
    ss.vesting = dict(
        n_employees=int(n_emp), turnover_pct=turnover_pct, forfeit_pct=forfeit_pct,
        expected_leavers=int(expected_leavers), vesting_period_years=float(vesting_yrs),
        service_condition=service_ok, performance_condition=perf_ok,
        expected_vest_pct=float(expected_vest_pct), expected_vested=float(expected_vested),
    )
    # propagate
    p["vesting_period_years"] = float(vesting_yrs)
    p["forfeiture_rate"] = 1.0 - expected_vest_pct / 100.0
    p["expected_vested"] = float(expected_vested)

    kpi_grid([
        ("Expected vested", fmt_money(expected_vested, 0), f"{expected_vest_pct:.1f}% of granted"),
        ("Forfeiture rate", fmt_pct(forfeit_pct/100, 2), "Updated"),
        ("Vesting (years)", f"{vesting_yrs:.2f}", "Service period"),
    ])
    st.info("Equity-settled: grant-date FV fixed. Only the expected number of instruments is updated. "
            "Cash-settled: FV is remeasured at each reporting date.")

# ============================================================
# TAB 5 — First-year accounting
# ============================================================
with tabs[4]:
    st.subheader("First-year accounting")
    p, b, v = ss.program, ss.bs, ss.vesting

    c1, c2, c3 = st.columns(3)
    with c1:
        months = st.number_input("Months active in first reporting year", min_value=0, max_value=12, value=12, key="fy_months")
    with c2:
        fv_default = float(b.get("selected_fv", 0.0)) or 0.0
        fv_per = st.number_input("Grant-date FV per option", min_value=0.0,
                                 value=fv_default, step=0.01, format="%.4f", key="fy_fv_per")
    with c3:
        vested_default = float(v.get("expected_vested", p.get("expected_vested", 0.0)))
        expected_vested_in = st.number_input("Expected vested instruments", min_value=0.0,
                                             value=vested_default, step=1.0, key="fy_expected_vested")

    program_type = p.get("program_type", "equity")
    has_liability = False
    cash_alt = equity_alt = liability_val = 0.0
    if program_type == "choice":
        st.markdown("##### Employee choice — compound instrument inputs")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            has_liability = st.checkbox("Present obligation to settle in cash?", value=True, key="fy_has_liability")
        with c2:
            liability_val = st.number_input("Cash-settled liability value", min_value=0.0, value=0.0, key="fy_liability_val")
        with c3:
            cash_alt = st.number_input("Cash alternative value", min_value=0.0, value=0.0, key="fy_cash_alt")
        with c4:
            equity_alt = st.number_input("Equity alternative value", min_value=0.0, value=0.0, key="fy_equity_alt")

    if st.button("Compute first-year accounting", key="btn_compute_first_year"):
        try:
            val = compute_valuation(ValuationInputs(
                program_type=program_type,
                fair_value_per_option=fv_per,
                options_granted=int(expected_vested_in),
                forfeiture_rate=0.0,
                vesting_period_years=float(p.get("vesting_period_years", 1.0) or 1.0),
                months_in_first_year=int(months),
                has_liability=has_liability,
                liability_value=liability_val,
                cash_alternative_value=cash_alt,
                equity_alternative_value=equity_alt,
            ))
            entries = accounting_entries(program_type, val)
            ss.first_year = {
                "inputs": {"months": months, "fv_per": fv_per, "expected_vested": expected_vested_in,
                           "has_liability": has_liability, "liability_value": liability_val,
                           "cash_alternative_value": cash_alt, "equity_alternative_value": equity_alt},
                "valuation": val, "entries": entries,
            }
        except Exception as e:
            st.error(f"Error: {e}")

    fy = ss.first_year
    if fy:
        val = fy["valuation"]
        kpi_grid([
            ("Total fair value", fmt_money(val["total_fair_value"], 2), "Award FV at grant"),
            ("Annual expense", fmt_money(val["annual_expense"], 2), "Straight-line over vesting"),
            ("First-year expense", fmt_money(val["first_year_expense"], 2), f"{int(fy['inputs']['months'])} months"),
            ("Liability", fmt_money(val["liability_amount"], 2), "If cash / compound"),
            ("Equity reserve", fmt_money(val["equity_reserve_amount"], 2), "If equity / compound"),
        ])
        st.markdown("##### Accounting entries")
        st.dataframe(pd.DataFrame(fy["entries"]), use_container_width=True)

# ============================================================
# TAB 6 — Subsequent period
# ============================================================
with tabs[5]:
    st.subheader("Subsequent period valuation")
    subtype_label = st.selectbox("Award type for subsequent period",
                                 list(PROGRAM_TYPES.keys()),
                                 index=list(PROGRAM_TYPES.values()).index(
                                     ss.program.get("program_type", "equity")), key="sub_award_type")
    subtype = PROGRAM_TYPES[subtype_label]
    p = ss.program

    if subtype == "equity":
        c1, c2, c3 = st.columns(3)
        with c1:
            fv = st.number_input("Grant-date FV per option",
                                 value=float(ss.bs.get("selected_fv", 0.0)) or 0.0, format="%.4f", key="sub_eq_fv")
            granted = st.number_input("Original instruments granted", min_value=0,
                                      value=int(p.get("total_granted", 0)), key="sub_eq_granted")
        with c2:
            upd_forf = st.number_input("Updated forfeiture rate (%)", min_value=0.0, max_value=100.0,
                                       value=float(p.get("forfeiture_rate", 0.1)) * 100, step=0.5, key="sub_eq_upd_forf")
            vest_yrs = st.number_input("Vesting period (years)", min_value=0.01,
                                       value=float(p.get("vesting_period_years", 3.0)), key="sub_eq_vest_yrs")
        with c3:
            cum_service = st.number_input("Cumulative service period completed (years)",
                                          min_value=0.0, value=1.0, step=0.25, key="sub_eq_cum_service")
            cum_prior = st.number_input("Cumulative expense recognized in prior periods",
                                        min_value=0.0, value=0.0, key="sub_eq_cum_prior")

        if st.button("Compute equity subsequent", key="btn_sub_eq"):
            res = equity_subsequent(EquitySubsequentInputs(
                grant_date_fv_per_option=fv, instruments_granted=int(granted),
                updated_forfeiture_rate=upd_forf/100,
                vesting_period_years=vest_yrs,
                cumulative_service_years=cum_service,
                cumulative_expense_prior=cum_prior,
            ))
            entries = equity_subsequent_entries(res["current_period_expense"])
            ss.subsequent = {"type": "equity", "result": res, "entries": entries}

    elif subtype == "cash":
        c1, c2, c3 = st.columns(3)
        with c1:
            S0 = st.number_input("Current share price S₀", min_value=0.0001,
                                 value=float(ss.bs.get("S0", 100.0)), key="sub_cash_S0")
            K = st.number_input("Current strike K", min_value=0.0001,
                                value=float(ss.bs.get("K", 100.0)), key="sub_cash_K")
            sigma_pct = st.number_input("Current volatility σ (%)", min_value=0.01,
                                        value=float(ss.bs.get("sigma", 0.3))*100, step=1.0, key="sub_cash_sigma_pct")
        with c2:
            r_pct = st.number_input("Risk-free r (%)", value=float(ss.bs.get("r", 0.05))*100, step=0.25, key="sub_cash_r_pct")
            q_pct = st.number_input("Dividend yield q (%)", value=float(ss.bs.get("q", 0.0))*100, step=0.25, key="sub_cash_q_pct")
            T_rem = st.number_input("Remaining expected life (years)", min_value=0.01,
                                    value=float(ss.bs.get("T", 3.0)), key="sub_cash_T_rem")
        with c3:
            outstanding = st.number_input("Instruments outstanding", min_value=0,
                                          value=int(p.get("total_granted", 0)), key="sub_cash_outstanding")
            upd_forf = st.number_input("Updated forfeiture rate (%)", min_value=0.0, max_value=100.0,
                                       value=float(p.get("forfeiture_rate", 0.1))*100, step=0.5, key="sub_cash_upd_forf")
            opening_liab = st.number_input("Opening liability (prior period)", min_value=0.0, value=0.0, key="sub_cash_opening_liab")
        c4, c5 = st.columns(2)
        with c4:
            vest_progress = st.slider("Vesting service progress", 0.0, 1.0, 0.5, 0.05, key="sub_cash_vest_progress")
        with c5:
            cash_paid = st.number_input("Cash paid / settled during period", min_value=0.0, value=0.0, key="sub_cash_paid")

        if st.button("Compute cash subsequent", key="btn_sub_cash"):
            try:
                bs = black_scholes(BSInputs(S0=S0, K=K, r=r_pct/100, q=q_pct/100,
                                            sigma=sigma_pct/100, T=T_rem))
                fv_now = bs.call  # cash-settled SARs typically priced as call
                res = cash_subsequent(CashSubsequentInputs(
                    current_fv_per_option=fv_now, instruments_outstanding=int(outstanding),
                    updated_forfeiture_rate=upd_forf/100, vesting_progress=vest_progress,
                    opening_liability=opening_liab, cash_paid_during_period=cash_paid,
                ))
                ss.subsequent = {"type": "cash", "result": res,
                                 "entries": cash_subsequent_entries(res)}
            except Exception as e:
                st.error(f"Error: {e}")

    else:  # choice
        c1, c2, c3 = st.columns(3)
        with c1:
            has_obl = st.checkbox("Present obligation to settle in cash?", value=True, key="sub_choice_has_obl")
            opening_liab = st.number_input("Opening liability", min_value=0.0, value=0.0, key="sub_choice_opening_liab")
        with c2:
            cash_fv = st.number_input("Updated cash alternative FV / instr.", min_value=0.0, value=0.0, key="sub_choice_cash_fv")
            equity_fv = st.number_input("Updated equity alternative FV / instr.", min_value=0.0, value=0.0, key="sub_choice_equity_fv")
        with c3:
            upd_vested = st.number_input("Updated expected vested instruments", min_value=0.0,
                                         value=float(p.get("expected_vested", 0.0)), key="sub_choice_upd_vested")
            vest_progress = st.slider("Vesting service progress", 0.0, 1.0, 0.5, 0.05, key="sub_choice_vest_progress")
        cash_paid = st.number_input("Cash paid during period", min_value=0.0, value=0.0, key="sub_choice_cash_paid")
        st.warning("Classification of compound instruments depends on the exact IFRS 2 terms — confirm with auditors.")

        if st.button("Compute choice subsequent", key="btn_sub_choice"):
            res = choice_subsequent(ChoiceSubsequentInputs(
                has_cash_obligation=has_obl, opening_liability=opening_liab,
                updated_cash_fv=cash_fv, updated_equity_fv=equity_fv,
                updated_expected_vested=upd_vested, vesting_progress=vest_progress,
                cash_paid=cash_paid,
            ))
            ss.subsequent = {"type": "choice", "result": res,
                             "entries": choice_subsequent_entries(res)}

    sub = ss.subsequent
    if sub:
        st.markdown("##### Result")
        st.dataframe(pd.DataFrame([{"Metric": k, "Value": v} for k, v in sub["result"].items()]),
                     use_container_width=True)
        st.markdown("##### Accounting entries")
        st.dataframe(pd.DataFrame(sub["entries"]), use_container_width=True)

# ============================================================
# TAB 7 — Summary & export
# ============================================================
with tabs[6]:
    st.subheader("Executive summary")
    p, b, fy, sub = ss.program, ss.bs, ss.first_year, ss.subsequent
    val = fy.get("valuation", {}) if fy else {}
    sub_res = sub.get("result", {}) if sub else {}

    kpi_grid([
        ("Program type", p.get("program_label", "—"), p.get("instrument_type", "—")),
        ("Fair value / option", fmt_money(b.get("selected_fv", 0.0), 4), b.get("option_type", "—")),
        ("Expected vested", fmt_money(p.get("expected_vested", 0.0), 0), "Updated"),
        ("Total award FV", fmt_money(val.get("total_fair_value", 0.0), 2), "At grant"),
        ("First-year expense", fmt_money(val.get("first_year_expense", 0.0), 2), "P&L impact"),
        ("Current period expense", fmt_money(sub_res.get("current_period_expense", 0.0), 2), "Subsequent"),
        ("Closing liability", fmt_money(sub_res.get("closing_liability", val.get("liability_amount", 0.0)), 2), "BS"),
        ("Closing equity reserve", fmt_money(sub_res.get("equity_reserve_closing", val.get("equity_reserve_amount", 0.0)), 2), "BS"),
    ])

    st.markdown("#### Inputs & assumptions")
    inputs_table = {**p, **{f"bs_{k}": v for k, v in b.items()},
                    **{f"vol_{k}": v for k, v in ss.vol.items()},
                    **{f"vest_{k}": v for k, v in ss.vesting.items()}}
    st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in inputs_table.items()]),
                 use_container_width=True)

    if fy:
        st.markdown("#### First-year accounting entries")
        st.dataframe(pd.DataFrame(fy["entries"]), use_container_width=True)
    if sub:
        st.markdown(f"#### Subsequent period — {sub['type']}")
        st.dataframe(pd.DataFrame(sub["entries"]), use_container_width=True)

    st.markdown("---")
    if st.button("📥 Build Excel report", key="btn_build_excel"):
        try:
            xlsx_bytes = build_excel(
                inputs=inputs_table,
                bs_calc=b,
                valuation=val,
                entries=(fy.get("entries", []) if fy else []) + (sub.get("entries", []) if sub else []),
                historical_prices=ss.historical_prices,
                log_returns=ss.log_returns,
                volatility_info=ss.vol,
            )
            st.download_button("Download Excel", data=xlsx_bytes,
                               file_name="sbp_valuation_report.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"Export error: {e}")
