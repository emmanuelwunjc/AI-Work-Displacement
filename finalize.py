"""
finalize.py — Three fixes before dashboard build:
  1. Fix "Other" sector bucket (165 → small) using IMPLAN code ranges as fallback
  2. Drop 23 zero-employment placeholder rows (* Not an industry, govt payroll, etc.)
  3. Pre-compute DiD pairs for the DiD lab view
  4. Rebuild dashboard.json clean
"""

import pandas as pd
import json, os

OUT = "output"
df = pd.read_csv(f"{OUT}/industry_master.csv")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — Drop placeholder rows (zero employment + "Not an industry")
# ─────────────────────────────────────────────────────────────────────────────

before = len(df)
df = df[~df["Industry"].str.contains(r"\* Not an industry", na=False)]
df = df[df["Pre_Emp_Total"] > 0]   # drop all zero-employment rows
after = len(df)
print(f"Dropped {before - after} placeholder rows → {after} real industries")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 — Reassign "Other" using IMPLAN code ranges
# IMPLAN codes follow BEA I-O ordering; ranges are well-established
# ─────────────────────────────────────────────────────────────────────────────

def code(name):
    try:
        return int(str(name).split(" - ")[0].strip())
    except:
        return -1

code_sector_map = [
    # (lo, hi_inclusive, sector)
    (1,   17,  "Agriculture & Natural Resources"),
    (18,  26,  "Agriculture & Natural Resources"),   # forestry/fishing
    (27,  34,  "Mining & Extraction"),
    (35,  44,  "Energy & Utilities"),
    (45,  65,  "Construction"),
    (66,  100, "Manufacturing — Food & Beverage"),
    (101, 120, "Manufacturing — Textiles & Apparel"),
    (121, 144, "Manufacturing — Vehicles & Other Durable"),  # wood/paper/print
    (145, 177, "Manufacturing — Chemicals & Pharma"),
    (178, 210, "Manufacturing — Vehicles & Other Durable"),  # plastics/rubber/glass/concrete
    (211, 260, "Manufacturing — Metals & Machinery"),
    (261, 290, "Manufacturing — Electronics & Tech"),
    (291, 340, "Manufacturing — Vehicles & Other Durable"),  # vehicles/misc manuf
    (341, 368, "Wholesale Trade"),
    (369, 401, "Retail Trade"),
    (402, 410, "Transportation & Logistics"),
    (411, 420, "Information & Technology"),
    (421, 430, "Finance & Insurance"),
    (431, 440, "Real Estate"),
    (441, 460, "Professional & Business Services"),
    (461, 470, "Professional & Business Services"),  # admin/support
    (471, 480, "Education"),
    (481, 495, "Healthcare & Social Assistance"),
    (496, 505, "Arts, Entertainment & Recreation"),
    (506, 515, "Personal Services & Repair"),
    (516, 528, "Government & Non-profit"),
]

def fix_sector(row):
    if row["Sector"] != "Other":
        return row["Sector"]
    c = code(row["Industry"])
    for lo, hi, sec in code_sector_map:
        if lo <= c <= hi:
            return sec
    return "Other"

df["Sector"] = df.apply(fix_sector, axis=1)

other_remaining = (df["Sector"] == "Other").sum()
print(f"After code-range fix → {other_remaining} industries still 'Other'")
if other_remaining > 0:
    print(df[df["Sector"]=="Other"]["Industry"].tolist())

# ─────────────────────────────────────────────────────────────────────────────
# FIX 3 — Pre-compute DiD pairs
# Treated = industry with high AI exposure; Control = plausible counterfactual
# ─────────────────────────────────────────────────────────────────────────────

def get(name):
    row = df[df["Industry"].str.contains(name, case=False)]
    if row.empty:
        return None
    return row.iloc[0]

did_pairs = [
    # ── AV (Current) Wave ─────────────────────────────────────────────────────
    {
        "pair": "Trucking vs Couriers",
        "treated_name": "Truck transportation",
        "control_name": "Couriers and messengers",
        "rationale": "Both Routine Manual — autonomous vehicles displace long-haul truckers while last-mile courier demand grows; clean AV-only counterfactual within freight.",
        "wave": "Current (AV)",
    },
    {
        "pair": "Transit & Ground Passenger vs Postal Service",
        "treated_name": "Transit and ground passenger transportation",
        "control_name": "Postal service",
        "rationale": "Both RM/human-operated transport corridors; AV threatens bus and shuttle drivers while postal delivery is growing from e-commerce and not yet AV-automated.",
        "wave": "Current (AV)",
    },
    # ── LLM (Next) Wave ───────────────────────────────────────────────────────
    {
        "pair": "Insurance Agencies vs Landscaping",
        "treated_name": "Insurance agencies, brokerages",
        "control_name": "Landscape and horticultural",
        "rationale": "Both classified RC (Routine Cognitive) — insurance is pure text-and-data work (claims, forms, quotes) while landscaping is site-specific physical labor. Same ALM category, divergent LLM exposure reveals within-RC heterogeneity.",
        "wave": "LLM (Next)",
    },
    {
        "pair": "Employment Services vs Residential Mental Health",
        "treated_name": "Employment services",
        "control_name": "Residential mental health",
        "rationale": "Staffing agencies (candidate screening, job matching, placement coordination) are prime LLM targets for automation; residential care workers require physical presence and human empathy that LLMs cannot substitute.",
        "wave": "LLM (Next)",
    },
    {
        "pair": "Depository Credit (Banks) vs Nursing Care",
        "treated_name": "Monetary authorities and depository credit",
        "control_name": "Nursing and community care",
        "rationale": "Bank back-office (loan processing, teller transactions, document review) is RC and highly automatable; nursing requires touch, continuous observation, and contextual judgment in physical settings — a natural AI vs. non-AI split.",
        "wave": "LLM (Next)",
    },
]

did_records = []
for p in did_pairs:
    tr = get(p["treated_name"])
    ct = get(p["control_name"])
    if tr is None or ct is None:
        print(f"  SKIP (not found): {p['pair']}")
        continue
    pre_tr  = tr["Pre_Emp_Total"]
    post_tr = tr["Post_Emp_Total"]
    pre_ct  = ct["Pre_Emp_Total"]
    post_ct = ct["Post_Emp_Total"]
    att = (post_tr - pre_tr) - (post_ct - pre_ct)
    did_records.append({
        "pair":           p["pair"],
        "rationale":      p["rationale"],
        "wave":           p["wave"],
        "treated":        tr["Industry"],
        "control":        ct["Industry"],
        "treated_pre":    round(pre_tr, 0),
        "treated_post":   round(post_tr, 0),
        "treated_chg":    round(post_tr - pre_tr, 0),
        "control_pre":    round(pre_ct, 0),
        "control_post":   round(post_ct, 0),
        "control_chg":    round(post_ct - pre_ct, 0),
        "ATT":            round(att, 0),
        "ATT_pct":        round(att / pre_tr * 100, 3),
    })
    print(f"  {p['pair']}: ATT = {att:,.0f} jobs")

did_df = pd.DataFrame(did_records)
did_df.to_csv(f"{OUT}/did_pairs.csv", index=False)
print(f"\n→ {OUT}/did_pairs.csv  ({len(did_df)} pairs)")

# ─────────────────────────────────────────────────────────────────────────────
# REBUILD — sector summary + master CSV + dashboard JSON
# ─────────────────────────────────────────────────────────────────────────────

# Fill nulls with 0 for pct columns
df["PctChange_Employment"]  = df["PctChange_Employment"].fillna(0)
df["PctChange_Output"]      = df["PctChange_Output"].fillna(0)
df["Impact_Per1000"]        = df["Impact_Per1000"].fillna(0)
df["Output_Per_Worker"]     = df["Output_Per_Worker"].fillna(0)

df.to_csv(f"{OUT}/industry_master.csv", index=False)

# Sector summary
sec_sum = df.groupby("Sector").agg(
    Industries=("Industry","count"),
    Pre_Emp=("Pre_Emp_Total","sum"),
    Job_Change=("Change_Employment","sum"),
    Pre_Output=("Pre_Out_Total","sum"),
    Avg_Risk=("AI_Risk_Score","mean"),
    Total_Exposure=("Exposure","sum"),
).round(2).reset_index()
sec_sum["Pct_Change"]    = (sec_sum["Job_Change"] / sec_sum["Pre_Emp"] * 100).round(3)
sec_sum["Change_Per1000"]= (sec_sum["Job_Change"] / sec_sum["Pre_Emp"] * 1000).round(2)
sec_sum = sec_sum.sort_values("Job_Change")
sec_sum.to_csv(f"{OUT}/sector_summary.csv", index=False)

# Cross-tabs
ct_emp = df.pivot_table(values="Pre_Emp_Total",    index="Sector", columns="ALM_Category", aggfunc="sum", fill_value=0).round(0).astype(int)
ct_chg = df.pivot_table(values="Change_Employment",index="Sector", columns="ALM_Category", aggfunc="sum", fill_value=0).round(0).astype(int)
ct_emp["TOTAL"] = ct_emp.sum(axis=1)
ct_chg["TOTAL"] = ct_chg.sum(axis=1)
ct_emp = ct_emp.sort_values("TOTAL", ascending=False)
ct_chg = ct_chg.reindex(ct_emp.index)
ct_emp.to_csv(f"{OUT}/crosstab_sector_alm_employment.csv")
ct_chg.to_csv(f"{OUT}/crosstab_sector_alm_change.csv")

# Cognitive 2-way crosstab
ct_cog = df.groupby(["Sector","Is_Cognitive"]).agg(
    Emp=("Pre_Emp_Total","sum"),
    Chg=("Change_Employment","sum"),
    N=("Industry","count"),
).round(1).reset_index()
ct_cog.to_csv(f"{OUT}/crosstab_sector_cognitive_long.csv", index=False)

# Dashboard JSON
records = []
for _, row in df.iterrows():
    records.append({
        "id":   row["Industry"].split(" - ")[0].strip(),
        "name": (" - ".join(row["Industry"].split(" - ")[1:])).strip() if " - " in row["Industry"] else row["Industry"],
        "full": row["Industry"],
        "sector":      row["Sector"],
        "alm":         row["ALM_Category"],
        "alm_label":   row["ALM_Label"],
        "is_cognitive":bool(row["Is_Cognitive"]),
        "risk":        round(float(row["AI_Risk_Score"]), 3),
        "exposure":    round(float(row["Exposure"]), 0),
        "pre_emp":     round(float(row["Pre_Emp_Total"]), 1),
        "post_emp":    round(float(row["Post_Emp_Total"]), 1),
        "chg_emp":     round(float(row["Change_Employment"]), 1),
        "pct_emp":     round(float(row["PctChange_Employment"]), 4),
        "per1000":     round(float(row["Impact_Per1000"]), 2),
        "pre_emp_d":   round(float(row["Pre_Emp_Direct"]), 1),
        "pre_emp_i":   round(float(row["Pre_Emp_Indirect"]), 1),
        "pre_emp_ind": round(float(row["Pre_Emp_Induced"]), 1),
        "post_emp_d":  round(float(row["Post_Emp_Direct"]), 1),
        "post_emp_i":  round(float(row["Post_Emp_Indirect"]), 1),
        "post_emp_ind":round(float(row["Post_Emp_Induced"]), 1),
        "pre_out":     round(float(row["Pre_Out_Total"]), 0),
        "post_out":    round(float(row["Post_Out_Total"]), 0),
        "chg_out":     round(float(row["Change_Output"]), 0),
        "pct_out":     round(float(row["PctChange_Output"]), 4),
        "out_per_worker": round(float(row["Output_Per_Worker"]), 0),
        "llm_shock_rate": round(float(row["LLM_Shock_Rate"]), 3),
        "llm_chg_emp":    round(float(row["LLM_Job_Change"]), 1),
        "llm_post_emp":   round(float(row["LLM_Post_Emp"]), 1),
    })

sector_records = json.loads(sec_sum.to_json(orient="records"))

dashboard = {
    "meta": {
        "model": "IMPLAN I-O 2024",
        "baseline": "Pre-AI 2024",
        "n_industries": len(records),
        "n_sectors": len(sector_records),
        "data_gap": "Labor income and value added not available at industry level — only aggregate totals. Output used as proxy.",
        "llm_assumptions": {"NRC-A": -0.08, "NRC-I": -0.05, "RC": -0.15, "RM": 0.0, "NRM": 0.0, "source": "Acemoglu 2023"},
    },
    "summary": {
        "current_wave": {
            "pre_emp": 6586002, "post_emp": 6533771, "net_jobs": -52231,
            "pct": -0.7931, "labor_income_delta_B": -5, "output_delta_B": 0,
            "direct_chg": -69084, "indirect_chg": 41222, "induced_chg": -24368,
        },
        "llm_wave": {"net_jobs": round(df["LLM_Job_Change"].sum(), 0)},
    },
    "did_pairs":  did_records,
    "sectors":    sector_records,
    "industries": records,
}

with open(f"{OUT}/dashboard.json", "w") as f:
    json.dump(dashboard, f, separators=(",",":"))   # minified for browser

size_kb = os.path.getsize(f"{OUT}/dashboard.json") / 1024
print(f"\n→ {OUT}/dashboard.json  ({len(records)} industries, {size_kb:.1f} KB)")
print(f"→ {OUT}/industry_master.csv  ({len(df)} rows, {len(df.columns)} cols)")
print(f"→ {OUT}/sector_summary.csv  ({len(sec_sum)} sectors)")
print(f"\nFinal sector distribution:")
print(df["Sector"].value_counts().to_string())
