"""Utility helpers."""
from __future__ import annotations

import io
import pandas as pd


def parse_number(value) -> float:
    """Parse a number that may use a Polish decimal comma."""
    if value is None:
        raise ValueError("Empty value")
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(" ", "").replace("\xa0", "")
    if s == "":
        raise ValueError("Empty value")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")
    return float(s)


def coerce_numeric_series(series: pd.Series) -> pd.Series:
    def _conv(x):
        try:
            return parse_number(x)
        except Exception:
            return None
    return series.map(_conv).astype(float)


def read_uploaded_table(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    bio = io.BytesIO(data)
    if name.endswith(".csv"):
        for sep in [",", ";", "\t", "|"]:
            bio.seek(0)
            try:
                df = pd.read_csv(bio, sep=sep)
                if df.shape[1] >= 1:
                    return df
            except Exception:
                continue
        bio.seek(0)
        return pd.read_csv(bio)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(bio)
    raise ValueError("Unsupported file format. Please upload CSV or XLSX.")
