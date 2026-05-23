"""Excel export using xlsxwriter."""
from __future__ import annotations

import io
from typing import Optional
import pandas as pd


def build_excel(inputs: dict, bs_calc: dict, valuation: dict, entries: list,
                historical_prices: Optional[pd.DataFrame] = None,
                log_returns: Optional[pd.Series] = None,
                volatility_info: Optional[dict] = None) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        wb = writer.book
        bold = wb.add_format({"bold": True, "bg_color": "#1F2937", "font_color": "white"})
        money = wb.add_format({"num_format": "#,##0.00"})
        wrap = wb.add_format({"text_wrap": True, "valign": "top"})

        def _write_kv(df, sheet, key_w=32, val_w=22, val_fmt=None):
            df.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.sheets[sheet]
            ws.set_column(0, 0, key_w)
            if val_fmt is not None:
                ws.set_column(1, 1, val_w, val_fmt)
            else:
                ws.set_column(1, 1, val_w)
            for i, v in enumerate(df.columns):
                ws.write(0, i, v, bold)

        _write_kv(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in inputs.items()]),
                  "Inputs", key_w=38)

        if historical_prices is not None and not historical_prices.empty:
            historical_prices.to_excel(writer, sheet_name="Historical Prices", index=False)
            ws = writer.sheets["Historical Prices"]
            for i, v in enumerate(historical_prices.columns):
                ws.write(0, i, v, bold)
            ws.set_column(0, len(historical_prices.columns) - 1, 18)

        if log_returns is not None and len(log_returns) > 0:
            lr = log_returns.reset_index()
            lr.columns = ["Index", "Log return"]
            lr.to_excel(writer, sheet_name="Log Returns", index=False)
            ws = writer.sheets["Log Returns"]
            ws.set_column(0, 0, 12)
            ws.set_column(1, 1, 18, money)
            for i, v in enumerate(lr.columns):
                ws.write(0, i, v, bold)

        if volatility_info is not None:
            vinfo = {k: v for k, v in volatility_info.items() if k != "log_returns"}
            _write_kv(pd.DataFrame([{"Metric": k, "Value": v} for k, v in vinfo.items()]),
                      "Volatility", key_w=28)

        _write_kv(pd.DataFrame([{"Metric": k, "Value": v} for k, v in bs_calc.items()]),
                  "Black-Scholes", key_w=28, val_fmt=money)

        _write_kv(pd.DataFrame([{"Metric": k, "Value": v} for k, v in valuation.items()]),
                  "Valuation", val_fmt=money)

        df_e = pd.DataFrame(entries)
        df_e.to_excel(writer, sheet_name="Accounting Entries", index=False)
        ws = writer.sheets["Accounting Entries"]
        ws.set_column(0, 0, 38)
        ws.set_column(1, 2, 16, money)
        ws.set_column(3, 3, 60, wrap)
        for i, v in enumerate(df_e.columns):
            ws.write(0, i, v, bold)

    return buf.getvalue()
