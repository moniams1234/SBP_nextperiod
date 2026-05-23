"""Custom CSS for a premium, light finance dashboard look."""
from __future__ import annotations

import streamlit as st

CUSTOM_CSS = """
<style>
:root {
  --sbp-bg: #f6f8fb;
  --sbp-bg-2: #eef3f9;
  --sbp-surface: #ffffff;
  --sbp-surface-2: #f8fafc;
  --sbp-border: #d8e0ea;
  --sbp-text: #142033;
  --sbp-muted: #5f6f86;
  --sbp-accent: #2563eb;
  --sbp-accent-2: #0f766e;
  --sbp-gold: #b88a00;
  --sbp-soft-blue: #eaf2ff;
  --sbp-soft-gold: #fff7dc;
}

html, body, [data-testid="stAppViewContainer"] {
  background: linear-gradient(160deg, var(--sbp-bg) 0%, var(--sbp-bg-2) 100%) !important;
  color: var(--sbp-text) !important;
}

[data-testid="stHeader"] {
  background: rgba(246, 248, 251, 0.85) !important;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%) !important;
  border-right: 1px solid var(--sbp-border) !important;
}

[data-testid="stSidebar"] * {
  color: var(--sbp-text) !important;
}

.block-container {
  padding-top: 1.2rem;
  max-width: 1400px;
}

h1, h2, h3, h4, h5, h6,
p, span, label, div, li,
.stMarkdown, .stText, .stCaption {
  color: var(--sbp-text) !important;
}

small, .caption, [data-testid="stCaptionContainer"], .help {
  color: var(--sbp-muted) !important;
}

.sbp-hero {
  background: linear-gradient(135deg, #ffffff 0%, #eaf2ff 55%, #f4fbfa 100%);
  border: 1px solid var(--sbp-border);
  border-radius: 18px;
  padding: 24px 28px;
  margin-bottom: 18px;
  box-shadow: 0 10px 28px rgba(20, 32, 51, .08);
}
.sbp-hero h1 {
  margin: 0;
  font-size: 30px;
  color: #0f172a !important;
}
.sbp-hero p {
  color: var(--sbp-muted) !important;
  margin: 6px 0 0;
}

.sbp-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 14px;
  margin: 8px 0 16px;
}
.sbp-kpi {
  background: #ffffff;
  border: 1px solid var(--sbp-border);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 8px 22px rgba(20, 32, 51, .07);
}
.sbp-kpi .label {
  color: var(--sbp-muted) !important;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.sbp-kpi .value {
  color: #0f172a !important;
  font-size: 23px;
  font-weight: 750;
  margin-top: 4px;
}
.sbp-kpi .sub {
  color: var(--sbp-muted) !important;
  font-size: 12px;
  margin-top: 2px;
}

.sbp-card {
  background: #ffffff;
  border: 1px solid var(--sbp-border);
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 14px;
  box-shadow: 0 8px 22px rgba(20, 32, 51, .06);
}

.sbp-disclaimer {
  background: var(--sbp-soft-gold);
  border: 1px solid #f0d98c;
  color: #5b4300 !important;
  border-radius: 13px;
  padding: 12px 16px;
  font-size: 13px;
  margin-bottom: 14px;
}
.sbp-disclaimer strong {
  color: #4a3600 !important;
}

div[data-testid="stTabs"] button[role="tab"] {
  background: transparent !important;
  color: var(--sbp-muted) !important;
  border-bottom: 2px solid transparent;
  padding: 10px 14px;
  font-weight: 650;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color: var(--sbp-accent) !important;
  border-bottom: 3px solid var(--sbp-accent);
}

.stButton>button, .stDownloadButton>button {
  background: linear-gradient(135deg, var(--sbp-accent), var(--sbp-accent-2)) !important;
  color: white !important;
  border: none !important;
  border-radius: 11px !important;
  padding: 10px 18px !important;
  font-weight: 700 !important;
  box-shadow: 0 8px 18px rgba(37,99,235,.24) !important;
}
.stButton>button:hover, .stDownloadButton>button:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}

/* Make all widgets clearly readable on light background */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div,
.stTextArea textarea {
  background: #ffffff !important;
  color: var(--sbp-text) !important;
  border-color: #cbd5e1 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
  color: #94a3b8 !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul,
[role="listbox"] {
  background: #ffffff !important;
  color: var(--sbp-text) !important;
}

[data-baseweb="option"],
[data-baseweb="menu"] li,
[role="option"] {
  color: var(--sbp-text) !important;
  background: #ffffff !important;
}

[data-baseweb="option"]:hover,
[role="option"]:hover {
  background: #eaf2ff !important;
}

/* DataFrames and tables */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  background: #ffffff !important;
  border-radius: 12px;
  border: 1px solid var(--sbp-border);
  box-shadow: 0 6px 16px rgba(20, 32, 51, .05);
}

.stAlert {
  color: var(--sbp-text) !important;
}

hr {
  border-color: var(--sbp-border);
}

code {
  color: #0f172a !important;
  background: #e2e8f0 !important;
}
</style>
"""

def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="sbp-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def disclaimer() -> None:
    st.markdown(
        '<div class="sbp-disclaimer"><strong>Disclaimer:</strong> '
        'This tool is for educational and analytical purposes only. Final IFRS 2 '
        'classification and accounting treatment should be reviewed based on the legal '
        'terms of the share-based payment plan and confirmed with professional '
        'accounting advisors or auditors.</div>',
        unsafe_allow_html=True,
    )


def kpi_grid(items):
    """items: list of (label, value, sub)."""
    cards = "".join(
        f'<div class="sbp-kpi"><div class="label">{lab}</div>'
        f'<div class="value">{val}</div><div class="sub">{sub}</div></div>'
        for lab, val, sub in items
    )
    st.markdown(f'<div class="sbp-kpi-grid">{cards}</div>', unsafe_allow_html=True)


def fmt_money(x, decimals: int = 2) -> str:
    try:
        return f"{float(x):,.{decimals}f}"
    except Exception:
        return str(x)


def fmt_pct(x, decimals: int = 2) -> str:
    try:
        return f"{float(x)*100:,.{decimals}f}%"
    except Exception:
        return str(x)
