# lib/data_loader.py

import re
import pandas as pd
from lib.mapping import MACRO_MAP

ALL_SPECS = sum(MACRO_MAP.values(), [])

BIN_TRUE = {"✓", "✔", "1", 1, "sim", "yes", "x", "Sim", "Yes", "X", True}
BIN_FALSE = {"0", 0, "", None, False}

def detect_sep(sample: str) -> str:
    return ";" if sample.count(";") > sample.count(",") else ","

def to_binary(val):
    if val in BIN_TRUE: return 1
    if val in BIN_FALSE: return 0
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("sim", "yes", "x", "✔", "✓"): return 1
        if v.isdigit(): return 1 if int(v) != 0 else 0
    return 0

def compute_macro_count(row):
    return sum(1 for specs in MACRO_MAP.values() if row[specs].sum() > 0)

def load_csv(path: str) -> pd.DataFrame:
    # Detect separator
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        head = f.read(2048)
    sep = detect_sep(head)

    df = pd.read_csv(path, sep=sep, engine="python", encoding="utf-8")

    # Normalize column names
    df.columns = [re.sub(r"\s+", " ", c).strip() for c in df.columns]

    # Convert specialty columns to binary
    for code in ALL_SPECS:
        if code not in df.columns:
            df[code] = 0
        df[code] = df[code].apply(to_binary).astype(int)

    # Detect ANA column
    ana_col = None
    for c in df.columns:
        if "ana" in c.lower():
            ana_col = c
            break

    df["ANA"] = df[ana_col].apply(to_binary).astype(int) if ana_col else 0

    # Filter rows with no specialties
    df["spec_total"] = df[ALL_SPECS].sum(axis=1)
    df = df[df["spec_total"] > 0].copy()

    # Macro count
    df["macro_count"] = df.apply(compute_macro_count, axis=1)

    # Clean NaNs
    df = df.replace({pd.NA: "", "nan": "", "NaN": "", None: ""})

    return df
