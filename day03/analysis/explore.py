"""Prints 3 facts about PoshanGuide records using pandas. Run from day03/: python analysis/explore.py"""
import json
from pathlib import Path

import pandas as pd

df = pd.DataFrame(json.loads((Path(__file__).resolve().parent.parent / "data" / "sample_records.json").read_text(encoding="utf-8")))

print("Fact 1: total records =", len(df), "| distinct guidelines =", df["guideline_no"].nunique())
top = df["target_group"].value_counts()
print(f"Fact 2: most common target group = '{top.index[0]}' ({top.iloc[0]} records)")
with_num = (df["number_limit"].str.strip() != "").sum()
print(f"Fact 3: records with a numeric limit = {with_num} of {len(df)}")
