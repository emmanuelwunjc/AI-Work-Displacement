"""
wrangle.py — Scales Sheet1 template into real data from all Excel sheets.

Outputs (all in ./output/):
  summary_comparison.csv       — Pre vs Post totals (mirrors Sheet1 rows 1-8)
  industry_employment.csv      — Pre/Post employment by industry + change (mirrors Sheet1 rows 11-14 scaled)
  industry_output.csv          — Pre/Post output by industry + change
  impact_breakdown_pre.csv     — Direct/Indirect/Induced/Total for employment Pre (mirrors rows 17-20 template)
  impact_breakdown_post.csv    — Direct/Indirect/Induced/Total for employment Post
  impact_output_pre.csv        — Direct/Indirect/Induced/Total for output Pre
  impact_output_post.csv       — Direct/Indirect/Induced/Total for output Post
  combined_industry_full.csv   — Everything merged: Pre+Post employment+output per industry
  work_log.txt                 — Log of what was done and what each file is
"""

import pandas as pd
import os

EXCEL = "Macro Project.xlsx"
OUT = "output"
os.makedirs(OUT, exist_ok=True)

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

log("=== WRANGLE LOG ===")
log(f"Source: {EXCEL}")
log("")

# ── helpers ──────────────────────────────────────────────────────────────────

def read_summary(sheet_name):
    """Read Pre_E or Post_E — 5 rows, 9 cols. Returns tidy DataFrame."""
    df = pd.read_excel(EXCEL, sheet_name=sheet_name)
    df.columns = ["GroupName","EventName","ModelName","Impact",
                  "Employment","LaborIncome","ValueAdded","Output","TagName"]
    df = df.drop(columns=["TagName"])
    df["Employment"] = pd.to_numeric(df["Employment"], errors="coerce")
    df["LaborIncome"] = pd.to_numeric(df["LaborIncome"], errors="coerce")
    df["ValueAdded"]  = pd.to_numeric(df["ValueAdded"],  errors="coerce")
    df["Output"]      = pd.to_numeric(df["Output"],      errors="coerce")
    return df

def read_detail(sheet_name, value_col_prefix):
    """Read Pre_J/Post_J or Pre_O/Post_O.
    Returns tidy DataFrame with columns:
      Industry, Direct, Indirect, Induced, Total
    Drops the header row (index 0) and totals row (last row).
    """
    df = pd.read_excel(EXCEL, sheet_name=sheet_name, header=None)
    df.columns = ["RowNum", "Industry", "Direct", "Indirect", "Induced", "Total"]
    # Row 0 is the column-header row inside the sheet — drop it
    df = df.iloc[1:].copy()
    # Drop totals row (last row, Industry cell contains 'Total' or is NaN)
    last = df.iloc[-1]
    if pd.isna(last["Industry"]) or str(last["Industry"]).strip().lower() in ("total", "totals", ""):
        df = df.iloc[:-1]
    df = df.drop(columns=["RowNum"])
    df = df.dropna(subset=["Industry"])
    df["Industry"] = df["Industry"].astype(str).str.strip()
    for c in ["Direct","Indirect","Induced","Total"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df = df.rename(columns={
        "Direct":   f"{value_col_prefix}_Direct",
        "Indirect": f"{value_col_prefix}_Indirect",
        "Induced":  f"{value_col_prefix}_Induced",
        "Total":    f"{value_col_prefix}_Total",
    })
    return df.reset_index(drop=True)

# ── 1. Summary comparison (Sheet1 rows 1-8 analogue) ────────────────────────

log("Reading summary sheets (Pre_E, Post_E)…")
pre_e  = read_summary("Pre_E")
post_e = read_summary("Post_E")

# Label which rows are impact-type rows vs grand total
def label_impact(df):
    df = df.copy()
    df["ImpactLabel"] = df["Impact"].fillna("Total").astype(str)
    return df

pre_e  = label_impact(pre_e)
post_e = label_impact(post_e)

# Merge pre and post side by side
summary = pre_e[["ImpactLabel","Employment","LaborIncome","ValueAdded","Output"]].copy()
summary.columns = ["ImpactLabel","Pre_Employment","Pre_LaborIncome","Pre_ValueAdded","Pre_Output"]
post_vals = post_e[["ImpactLabel","Employment","LaborIncome","ValueAdded","Output"]].copy()
post_vals.columns = ["ImpactLabel","Post_Employment","Post_LaborIncome","Post_ValueAdded","Post_Output"]

summary = summary.merge(post_vals, on="ImpactLabel")
for m in ["Employment","LaborIncome","ValueAdded","Output"]:
    summary[f"Change_{m}"] = summary[f"Post_{m}"] - summary[f"Pre_{m}"]
    summary[f"PctChange_{m}"] = (summary[f"Change_{m}"] / summary[f"Pre_{m}"].replace(0, pd.NA) * 100).round(4)

summary.to_csv(f"{OUT}/summary_comparison.csv", index=False)
log(f"  → {OUT}/summary_comparison.csv  ({len(summary)} rows)")

# ── 2. Industry employment (Pre_J, Post_J) ──────────────────────────────────

log("Reading employment detail sheets (Pre_J, Post_J)…")
pre_j  = read_detail("Pre_J",  "Pre_Emp")
post_j = read_detail("Post_J", "Post_Emp")

emp = pre_j.merge(post_j, on="Industry", how="outer")
emp["Change_Employment"] = emp["Post_Emp_Total"] - emp["Pre_Emp_Total"]
emp["PctChange_Employment"] = (emp["Change_Employment"] / emp["Pre_Emp_Total"].replace(0, pd.NA) * 100).round(4)
emp = emp.sort_values("Change_Employment")  # most-displaced first

emp.to_csv(f"{OUT}/industry_employment.csv", index=False)
log(f"  → {OUT}/industry_employment.csv  ({len(emp)} industries)")

# ── 3. Industry output (Pre_O, Post_O) ──────────────────────────────────────

log("Reading output detail sheets (Pre_O, Post_O)…")
pre_o  = read_detail("Pre_O",  "Pre_Out")
post_o = read_detail("Post_O", "Post_Out")

out_df = pre_o.merge(post_o, on="Industry", how="outer")
out_df["Change_Output"] = out_df["Post_Out_Total"] - out_df["Pre_Out_Total"]
out_df["PctChange_Output"] = (out_df["Change_Output"] / out_df["Pre_Out_Total"].replace(0, pd.NA) * 100).round(4)
out_df = out_df.sort_values("Change_Output")

out_df.to_csv(f"{OUT}/industry_output.csv", index=False)
log(f"  → {OUT}/industry_output.csv  ({len(out_df)} industries)")

# ── 4. Impact breakdown tables (mirrors Sheet1 rows 17-20 template) ──────────

for label, df in [("pre", pre_j), ("post", post_j)]:
    fname = f"{OUT}/impact_breakdown_{label}.csv"
    df.to_csv(fname, index=False)
    log(f"  → {fname}  ({len(df)} industries)")

for label, df in [("pre", pre_o), ("post", post_o)]:
    fname = f"{OUT}/impact_output_{label}.csv"
    df.to_csv(fname, index=False)
    log(f"  → {fname}  ({len(df)} industries)")

# ── 5. Combined full table ───────────────────────────────────────────────────

log("Building combined full table…")
combined = emp.merge(out_df, on="Industry", how="outer")
combined.to_csv(f"{OUT}/combined_industry_full.csv", index=False)
log(f"  → {OUT}/combined_industry_full.csv  ({len(combined)} industries, {len(combined.columns)} columns)")

# ── 6. Work log ──────────────────────────────────────────────────────────────

log("")
log("=== OUTPUT FILE GUIDE ===")
file_guide = {
    "summary_comparison.csv":       "Mirrors Sheet1 rows 1-8. Pre vs Post totals for Employment, Labor Income, Value Added, Output — broken down by Direct/Indirect/Induced impact + grand Total. Includes absolute change and % change columns.",
    "industry_employment.csv":      "Mirrors Sheet1 rows 11-14 scaled to all 528 industries. Pre and Post employment (Direct/Indirect/Induced/Total) per industry, sorted by largest job losses first.",
    "industry_output.csv":          "Same structure as industry_employment but for economic Output in dollars. Sorted by largest output change.",
    "impact_breakdown_pre.csv":     "Mirrors Sheet1 rows 17-20 template for the Pre-AI scenario. Raw employment impact breakdown (Direct/Indirect/Induced/Total) for each of 528 industries.",
    "impact_breakdown_post.csv":    "Same as impact_breakdown_pre but for Post-AI scenario.",
    "impact_output_pre.csv":        "Raw output impact breakdown (Direct/Indirect/Induced/Total) for each industry — Pre-AI scenario.",
    "impact_output_post.csv":       "Same as impact_output_pre but for Post-AI scenario.",
    "combined_industry_full.csv":   "Everything merged: all Pre+Post employment and output columns for all 528 industries in one wide table. Use this for analysis or visualization.",
}
for fname, desc in file_guide.items():
    log(f"\n  {fname}:\n    {desc}")

log_text = "\n".join(log_lines)
with open(f"{OUT}/work_log.txt", "w") as f:
    f.write(log_text)

print(f"\n  → {OUT}/work_log.txt")
print("\nDone.")
