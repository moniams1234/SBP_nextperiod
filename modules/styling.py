"""Custom CSS for a premium finance dashboard look."""
from __future__ import annotations

import streamlit as st

CUSTOM_CSS = """
<style>
:root {
  --sbp-bg: #0b1220;
  --sbp-surface: #111a2e;
  --sbp-surface-2: #16223d;
  --sbp-border: #1f2d4a;
  --sbp-text: #e6ecf5;
  --sbp-muted: #93a3bf;
  --sbp-accent: #4f8cff;
  --sbp-accent-2: #7c5cff;
  --sbp-gold: #d4af37;
}
html, body, [data-testid="stAppViewContainer"] {
  background: linear-gradient(160deg, #0b1220 0%, #0d1730 100%) !important;
  color: var(--sbp-text) !important;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0a1124 0%, #0f1a36 100%) !important;
  border-right: 1px solid var(--sbp-border);
}
[data-testid="stSidebar"] * { color: var(--sbp-text) !important; }
.block-container { padding-top: 1.2rem; max-width: 1400px; }
h1, h2, h3, h4 { color: var(--sbp-text) !important; letter-spacing: .2px; }

.sbp-hero {
  background: linear-gradient(135deg, rgba(79,140,255,.18), rgba(124,92,255,.10));
  border: 1px solid var(--sbp-border);
  border-radius: 16px; padding: 22px 26px; margin-bottom: 18px;
}
.sbp-hero h1 { margin: 0; font-size: 28px; }
.sbp-hero p { color: var(--sbp-muted); margin: 6px 0 0; }

.sbp-kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px,1fr)); gap: 14px; }
.sbp-kpi {
  background: var(--sbp-surface); border: 1px solid var(--sbp-border);
  border-radius: 14px; padding: 16px 18px; box-shadow: 0 6px 20px rgba(0,0,0,.25);
}
.sbp-kpi .label { color: var(--sbp-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.sbp-kpi .value { color: var(--sbp-text); font-size: 22px; font-weight: 700; margin-top: 4px; }
.sbp-kpi .sub { color: var(--sbp-muted); font-size: 12px; margin-top: 2px; }

.sbp-card {
  background: var(--sbp-surface); border: 1px solid var(--sbp-border);
  border-radius: 14px; padding: 18px 20px; margin-bottom: 14px;
}
.sbp-disclaimer {
  background: rgba(212,175,55,.08); border: 1px solid rgba(212,175,55,.4);
  color: #f3e6b3; border-radius: 12px; padding: 12px 16px; font-size: 13px; margin-bottom: 14px;
}
div[data-testid="stTabs"] button[role="tab"] {
  background: transparent; color: var(--sbp-muted);
  border-bottom: 2px solid transparent; padding: 10px 14px; font-weight: 600;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color: var(--sbp-text); border-bottom: 2px solid var(--sbp-accent);
}
.stButton>button, .stDownloadButton>button {
  background: linear-gradient(135deg, var(--sbp-accent), var(--sbp-accent-2));
  color: white; border: none; border-radius: 10px;
  padding: 10px 18px; font-weight: 600;
  box-shadow: 0 6px 18px rgba(79,140,255,.35);
}
.stButton>button:hover, .stDownloadButton>button:hover { filter: brightness(1.08); }
[data-testid="stDataFrame"], [data-testid="stTable"] {
  background: var(--sbp-surface) !important; border-radius: 12px; border: 1px solid var(--sbp-border);
}
hr { border-color: var(--sbp-border); }
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
