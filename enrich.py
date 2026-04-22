"""
enrich.py — Full enrichment pipeline.

Steps:
  1. Sector classification (NAICS-aligned, ~15 sectors)
  2. Improved cognitive classifier (fix defaults)
  3. Cross-tab: sector × cognitive category
  4. Per-1000-workers normalization
  5. Dashboard JSON export
  6. Next-wave LLM shock scenario
"""

import pandas as pd
import json, re, os

OUT = "output"
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(f"{OUT}/industry_cognitive.csv")
df = df[df["Industry"] != "Industry Display"].copy()
df["Industry"] = df["Industry"].astype(str).str.strip()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — SECTOR CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

sector_rules = [
    # Order matters — first match wins
    ("Agriculture & Natural Resources", [
        "farming", "ranching", "crop", "livestock", "dairy", "poultry", "aquaculture",
        "oilseed", "grain", "vegetable", "fruit", "tree nut", "cotton", "sugarcane",
        "hay", "tobacco farm", "nursery", "floriculture", "hog", "sheep", "goat",
        "logging", "fishing", "hunting", "forestry",
        "support activities for agriculture",
    ]),
    ("Mining & Extraction", [
        "oil and gas extraction", "coal mining", "iron ore", "copper", "gold",
        "uranium", "potash", "phosphate", "other metal ore",
        "stone mining", "sand", "gravel", "clay", "kaolin", "drilling oil",
        "support activities for mining",
    ]),
    ("Energy & Utilities", [
        "electric power", "natural gas distribution", "water supply",
        "sewage treatment", "steam and air-conditioning", "pipeline transportation",
    ]),
    ("Construction", [
        "construction of new", "construction of", "maintenance and repair construction",
        "residential", "nonresidential", "highway", "street", "bridge",
        "water and sewer", "communication infrastructure",
        "power and communication line",
        "masonry", "drywall", "insulation", "roofing",
        "plumbing", "heating", "air-conditioning",
        "painting", "wall covering", "flooring",
        "site preparation", "foundation",
        "building finishing", "building equipment",
        "specialty trade",
    ]),
    ("Manufacturing — Food & Beverage", [
        "animal food", "flour", "wet corn", "rice", "malt", "fats and oils",
        "breakfast cereal", "sugar", "confectionery",
        "fruit and vegetable canning", "dried and dehydrated",
        "fluid milk", "creamery butter", "cheese", "ice cream",
        "meat", "seafood", "poultry processing",
        "bread", "bakery", "tortilla",
        "snack food", "coffee", "tea", "flavoring",
        "mayonnaise", "dressing", "spice",
        "brewery", "winery", "distillery",
        "bottled and canned soft", "all other food",
    ]),
    ("Manufacturing — Textiles & Apparel", [
        "fiber, yarn", "broadwoven", "narrow fabric", "nonwoven", "knit fabric",
        "textile and fabric finishing", "fabric coating",
        "carpet and rug", "curtain", "linen", "textile bag",
        "rope, cordage", "hosiery", "underwear", "nightwear",
        "men's cut", "women's", "apparel",
        "leather", "footwear", "luggage",
    ]),
    ("Manufacturing — Chemicals & Pharma", [
        "petrochemical", "industrial gas", "synthetic dye",
        "pharmaceutical", "medicine manufacturing",
        "soap", "cleaning compound", "toilet preparation",
        "paint", "coating", "adhesive",
        "fertilizer", "pesticide", "agricultural chemical",
        "plastics material", "synthetic rubber",
        "all other chemical", "explosives",
        "tobacco manufacturing",
    ]),
    ("Manufacturing — Metals & Machinery", [
        "iron and steel", "steel product", "alumin", "copper rolling",
        "nonferrous metal", "foundry", "forging", "stamping",
        "cutlery", "hardware", "spring", "wire",
        "architectural metal", "boiler", "metal can",
        "heating equipment", "fabricated metal",
        "agriculture machinery", "construction machinery",
        "mining machinery", "industrial machinery",
        "engine", "turbine", "compressor", "pump",
        "material handling", "power transmission",
        "ventilation", "refrigeration",
        "metalworking machinery",
    ]),
    ("Manufacturing — Electronics & Tech", [
        "semiconductor", "electronic component", "printed circuit",
        "audio and video", "telephone apparatus",
        "broadcast", "search, detection", "electromedical",
        "computer storage", "computer terminal",
        "household appliance",
        "lighting equipment", "electrical equipment",
        "wiring device", "battery", "fiber optic",
        "measuring instrument", "laboratory instrument",
        "watch, clock",
    ]),
    ("Manufacturing — Vehicles & Other Durable", [
        "automobile", "light truck", "heavy duty truck", "motor vehicle body",
        "truck trailer", "motor home", "travel trailer",
        "aircraft", "ship", "boat",
        "railroad equipment", "military vehicle",
        "motorcycle", "bicycle",
        "furniture", "mattress",
        "wood product", "sawmill", "veneer", "plywood",
        "paper", "paperboard", "pulp mill",
        "printing", "support activities for printing",
        "glass", "cement", "concrete", "lime", "gypsum",
        "asphalt", "rubber product",
        "plastics product", "foam product",
        "sporting goods", "toy", "musical instrument",
        "medical equipment", "ophthalmic",
        "manufactured home", "office furniture",
        "industrial truck", "stacker",
        "all other manufacturing", "miscellaneous manufacturing",
    ]),
    ("Transportation & Logistics", [
        "truck transportation", "couriers and messengers",
        "warehousing and storage", "postal service",
        "air transportation", "rail transportation",
        "water transportation", "transit and ground",
        "scenic and sightseeing", "support activities for transportation",
    ]),
    ("Wholesale Trade", [
        "wholesale", "petroleum and petroleum products wholesale",
    ]),
    ("Retail Trade", [
        "retail", "gasoline store", "motor vehicle and parts dealer",
        "used merchandise",
    ]),
    ("Finance & Insurance", [
        "banking", "credit intermediation", "savings institution",
        "credit card", "consumer lending", "mortgage",
        "securities", "commodity contracts", "investment",
        "portfolio management", "investment advice",
        "trust, fiduciary",
        "insurance carriers", "insurance agency",
        "insurance funds", "annuity",
        "federal reserve", "monetary authority",
    ]),
    ("Real Estate", [
        "real estate", "owner-occupied housing", "tenant-occupied",
        "lessors of real estate", "offices of real estate",
    ]),
    ("Professional & Business Services", [
        "legal service", "accounting service",
        "architectural", "engineering service",
        "specialized design", "computer system design",
        "management consulting", "environmental consulting",
        "scientific research", "r&d",
        "advertising", "public relations",
        "market research", "photography",
        "translation", "veterinary",
        "other professional",
        "management of companies",
        "office administrative", "business support",
        "travel arrangement", "investigation and security",
        "services to buildings",
        "other support",
    ]),
    ("Information & Technology", [
        "software publisher", "data processing", "web hosting",
        "internet service", "other information service",
        "telephone", "telecommunications", "satellite",
        "radio broadcasting", "television broadcasting",
        "cable", "subscription programming",
        "wireless carrier", "other telecommunications",
        "newspaper", "periodical", "book publisher",
        "directory", "database publisher",
        "motion picture", "video", "sound recording",
    ]),
    ("Education", [
        "elementary", "secondary school",
        "junior college", "college", "university",
        "technical and trade school", "other educational",
    ]),
    ("Healthcare & Social Assistance", [
        "hospital", "nursing", "community care",
        "physician", "dentist", "optometrist",
        "chiropractor", "other ambulatory",
        "outpatient care", "medical laboratory",
        "home health care", "ambulance",
        "individual and family", "community food",
        "vocational rehabilitation", "child day care",
        "other social assistance",
    ]),
    ("Hospitality & Food Service", [
        "hotel", "motel", "resort",
        "rv park", "rooming and boarding",
        "casino hotel",
        "full-service restaurant", "limited-service restaurant",
        "special food service", "drinking place",
    ]),
    ("Arts, Entertainment & Recreation", [
        "performing arts", "spectator sports",
        "promoter of performing arts",
        "independent artist", "museum", "zoo",
        "amusement park", "gambling", "fitness",
        "bowling", "ski facility", "marina",
        "other amusement",
    ]),
    ("Personal Services & Repair", [
        "automotive repair", "car wash",
        "electronic equipment repair",
        "commercial equipment repair",
        "household goods repair",
        "personal care service", "beauty salon", "barber",
        "nail salon",
        "death care", "funeral",
        "coin-operated laundry", "dry-cleaning",
        "linen supply", "carpet cleaning",
        "photofinishing",
        "parking lot", "valet parking",
        "pet care", "tax preparation",
        "other personal service",
    ]),
    ("Government & Non-profit", [
        "federal government", "state government", "local government",
        "postal service",
        "religious", "civic", "social advocacy",
        "labor union", "professional organization",
        "political organization", "grant-making",
        "other membership",
    ]),
]

def assign_sector(name: str) -> str:
    n = name.lower()
    for sector, keywords in sector_rules:
        if any(k in n for k in keywords):
            return sector
    return "Other"

df["Sector"] = df["Industry"].apply(assign_sector)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — FIX COGNITIVE CLASSIFIER (find defaults, fix obvious ones)
# ─────────────────────────────────────────────────────────────────────────────

# Re-apply improved classifier with sector context
# Correct known mismatches using sector knowledge
sector_alm_overrides = {
    "Agriculture & Natural Resources":      ("NRM", 0.22),
    "Mining & Extraction":                  ("RM",  0.72),
    "Energy & Utilities":                   ("RM",  0.55),
    "Construction":                         ("NRM", 0.35),
    "Manufacturing — Food & Beverage":      ("RM",  0.78),
    "Manufacturing — Textiles & Apparel":   ("RM",  0.82),
    "Manufacturing — Chemicals & Pharma":   ("RM",  0.68),
    "Manufacturing — Metals & Machinery":   ("RM",  0.82),
    "Manufacturing — Electronics & Tech":   ("RM",  0.75),
    "Manufacturing — Vehicles & Other Durable": ("RM", 0.80),
    "Transportation & Logistics":           ("RM",  0.82),
    "Wholesale Trade":                      ("RC",  0.72),
    "Retail Trade":                         ("RC",  0.75),
    "Finance & Insurance":                  ("RC",  0.72),
    "Real Estate":                          ("NRC-I", 0.35),
    "Professional & Business Services":     ("NRC-A", 0.30),
    "Information & Technology":             ("NRC-A", 0.32),
    "Education":                            ("NRC-I", 0.25),
    "Healthcare & Social Assistance":       ("NRC-I", 0.38),
    "Hospitality & Food Service":           ("NRM", 0.28),
    "Arts, Entertainment & Recreation":     ("NRM", 0.20),
    "Personal Services & Repair":           ("NRM", 0.30),
    "Government & Non-profit":              ("NRC-I", 0.25),
    "Other":                                ("RC",  0.55),
}

cat_labels = {
    "NRC-A": "Non-routine Cognitive Analytic",
    "NRC-I": "Non-routine Cognitive Interpersonal",
    "RC":    "Routine Cognitive",
    "RM":    "Routine Manual",
    "NRM":   "Non-routine Manual",
}

def reclassify(row):
    s = row["Sector"]
    cat, risk = sector_alm_overrides.get(s, ("RC", 0.55))
    # Fine-tune specific high-value industries
    n = row["Industry"].lower()
    if "software" in n or "computer system" in n:    return "NRC-A", 0.28
    if "research" in n or "r&d" in n:               return "NRC-A", 0.22
    if "legal" in n or "law" in n:                   return "NRC-A", 0.32
    if "hospital" in n:                              return "NRC-I", 0.38
    if "physician" in n or "dentist" in n:           return "NRC-I", 0.32
    if "truck transportation" in n:                  return "RM",    0.95
    if "couriers" in n or "messenger" in n:          return "RM",    0.70
    if "warehousing" in n:                           return "RM",    0.75
    if "employment services" in n:                   return "RC",    0.60
    if "insurance" in n:                             return "RC",    0.72
    if "retail" in n:                                return "RC",    0.70
    return cat, risk

df["ALM_Category"], df["AI_Risk_Score"] = zip(*df.apply(reclassify, axis=1))
df["ALM_Label"]   = df["ALM_Category"].map(cat_labels)
df["Is_Cognitive"] = df["ALM_Category"].isin(["NRC-A", "NRC-I", "RC"])

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — CROSS-TAB: Sector × ALM Category
# ─────────────────────────────────────────────────────────────────────────────

# Employment cross-tab
ct_emp = df.pivot_table(
    values="Pre_Emp_Total",
    index="Sector",
    columns="ALM_Category",
    aggfunc="sum",
    fill_value=0,
).round(0).astype(int)

ct_emp["TOTAL"] = ct_emp.sum(axis=1)
ct_emp = ct_emp.sort_values("TOTAL", ascending=False)

# Job change cross-tab
ct_chg = df.pivot_table(
    values="Change_Employment",
    index="Sector",
    columns="ALM_Category",
    aggfunc="sum",
    fill_value=0,
).round(0).astype(int)
ct_chg["TOTAL"] = ct_chg.sum(axis=1)
ct_chg = ct_chg.reindex(ct_emp.index)

# Cognitive vs Manual cross-tab (simpler 2-way)
ct_cog = df.pivot_table(
    values=["Pre_Emp_Total", "Change_Employment"],
    index="Sector",
    columns="Is_Cognitive",
    aggfunc="sum",
    fill_value=0,
).round(0)
ct_cog.columns = ["Manual_PreEmp","Cog_PreEmp","Manual_Change","Cog_Change"]
ct_cog = ct_cog[["Cog_PreEmp","Cog_Change","Manual_PreEmp","Manual_Change"]]
ct_cog["Total_PreEmp"] = ct_cog["Cog_PreEmp"] + ct_cog["Manual_PreEmp"]
ct_cog["Total_Change"] = ct_cog["Cog_Change"]  + ct_cog["Manual_Change"]
ct_cog = ct_cog.sort_values("Total_PreEmp", ascending=False)

ct_emp.to_csv(f"{OUT}/crosstab_sector_alm_employment.csv")
ct_chg.to_csv(f"{OUT}/crosstab_sector_alm_change.csv")
ct_cog.to_csv(f"{OUT}/crosstab_sector_cognitive.csv")

print("=== CROSS-TAB: Employment by Sector × ALM Category ===")
print(ct_emp.to_string())
print("\n=== CROSS-TAB: Job Change by Sector × ALM Category ===")
print(ct_chg.to_string())
print("\n=== CROSS-TAB: Sector × Cognitive vs Manual ===")
print(ct_cog.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — PER-1000-WORKERS NORMALIZATION
# ─────────────────────────────────────────────────────────────────────────────

df["Impact_Per1000"]   = (df["Change_Employment"] / df["Pre_Emp_Total"] * 1000).round(2)
df["Output_Per_Worker"] = (df["Pre_Out_Total"]    / df["Pre_Emp_Total"]).round(0)
df["Exposure"]          = (df["AI_Risk_Score"]    * df["Pre_Emp_Total"]).round(0)

# Sector summaries
sec_sum = df.groupby("Sector").agg(
    Industries=("Industry","count"),
    Pre_Emp=("Pre_Emp_Total","sum"),
    Job_Change=("Change_Employment","sum"),
    Pre_Output=("Pre_Out_Total","sum"),
    Avg_Risk=("AI_Risk_Score","mean"),
    Total_Exposure=("Exposure","sum"),
).round(2).reset_index()
sec_sum["Pct_Change"] = (sec_sum["Job_Change"] / sec_sum["Pre_Emp"] * 100).round(3)
sec_sum["Change_Per1000"] = (sec_sum["Job_Change"] / sec_sum["Pre_Emp"] * 1000).round(2)
sec_sum = sec_sum.sort_values("Job_Change")
sec_sum.to_csv(f"{OUT}/sector_summary.csv", index=False)

print("\n=== SECTOR SUMMARY (sorted by job change) ===")
print(sec_sum[["Sector","Industries","Pre_Emp","Job_Change","Pct_Change","Change_Per1000","Avg_Risk"]].to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — NEXT-WAVE LLM SHOCK SCENARIO
# ─────────────────────────────────────────────────────────────────────────────
# Assumption: LLM automation hits RC (routine cognitive) at -15% employment,
# NRC-A at -8% (augmented but some substitution), NRC-I at -5% (trust barrier).
# RM and NRM unchanged in this wave (AV/robot wave already captured).
# Source framework: Acemoglu (2023) "The Simple Macroeconomics of AI"

llm_shock = {"NRC-A": -0.08, "NRC-I": -0.05, "RC": -0.15, "RM": 0.0, "NRM": 0.0}

df2 = df.copy()
df2["LLM_Shock_Rate"] = df2["ALM_Category"].map(llm_shock)
df2["LLM_Job_Change"]  = (df2["Pre_Emp_Total"] * df2["LLM_Shock_Rate"]).round(0)
df2["LLM_Post_Emp"]    = df2["Pre_Emp_Total"] + df2["LLM_Job_Change"]

llm_sum = df2.groupby("ALM_Category").agg(
    Pre_Emp=("Pre_Emp_Total","sum"),
    LLM_Change=("LLM_Job_Change","sum"),
    Current_Change=("Change_Employment","sum"),
).round(0).reset_index()
llm_sum["LLM_Pct"] = (llm_sum["LLM_Change"] / llm_sum["Pre_Emp"] * 100).round(2)
llm_sum["Current_Pct"] = (llm_sum["Current_Change"] / llm_sum["Pre_Emp"] * 100).round(2)

print("\n=== NEXT-WAVE LLM SCENARIO vs CURRENT AI WAVE ===")
print("Assumptions: RC -15%, NRC-A -8%, NRC-I -5%, RM/NRM unchanged")
print(llm_sum.to_string(index=False))
print(f"\nCurrent wave total net:  {df['Change_Employment'].sum():,.0f} jobs")
print(f"LLM wave total net:      {df2['LLM_Job_Change'].sum():,.0f} jobs")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — SAVE ENRICHED MASTER + JSON
# ─────────────────────────────────────────────────────────────────────────────

# Save enriched CSV
df2_out = df2.copy()
df2_out.to_csv(f"{OUT}/industry_master.csv", index=False)

# Build dashboard JSON
records = []
for _, row in df2_out.iterrows():
    records.append({
        "id":              row["Industry"].split(" - ")[0].strip(),
        "name":            " - ".join(row["Industry"].split(" - ")[1:]).strip() if " - " in row["Industry"] else row["Industry"],
        "full":            row["Industry"],
        "sector":          row["Sector"],
        "alm":             row["ALM_Category"],
        "alm_label":       row["ALM_Label"],
        "is_cognitive":    bool(row["Is_Cognitive"]),
        "risk":            round(float(row["AI_Risk_Score"]), 3),
        "exposure":        round(float(row["Exposure"]), 0),
        # Employment
        "pre_emp":         round(float(row["Pre_Emp_Total"]), 1),
        "post_emp":        round(float(row["Post_Emp_Total"]), 1),
        "chg_emp":         round(float(row["Change_Employment"]), 1),
        "pct_emp":         round(float(row["PctChange_Employment"]), 4),
        "per1000":         round(float(row["Impact_Per1000"]), 2),
        # Employment breakdown
        "pre_emp_d":       round(float(row["Pre_Emp_Direct"]), 1),
        "pre_emp_i":       round(float(row["Pre_Emp_Indirect"]), 1),
        "pre_emp_ind":     round(float(row["Pre_Emp_Induced"]), 1),
        "post_emp_d":      round(float(row["Post_Emp_Direct"]), 1),
        "post_emp_i":      round(float(row["Post_Emp_Indirect"]), 1),
        "post_emp_ind":    round(float(row["Post_Emp_Induced"]), 1),
        # Output
        "pre_out":         round(float(row["Pre_Out_Total"]), 0),
        "post_out":        round(float(row["Post_Out_Total"]), 0),
        "chg_out":         round(float(row["Change_Output"]), 0),
        "pct_out":         round(float(row["PctChange_Output"]), 4),
        "out_per_worker":  round(float(row["Output_Per_Worker"]), 0),
        # LLM scenario
        "llm_shock_rate":  round(float(row["LLM_Shock_Rate"]), 3),
        "llm_chg_emp":     round(float(row["LLM_Job_Change"]), 1),
        "llm_post_emp":    round(float(row["LLM_Post_Emp"]), 1),
    })

# Sector aggregates for the sector view
sector_records = []
for _, row in sec_sum.iterrows():
    sector_records.append({
        "sector":       row["Sector"],
        "n":            int(row["Industries"]),
        "pre_emp":      round(float(row["Pre_Emp"]), 0),
        "chg_emp":      round(float(row["Job_Change"]), 0),
        "pct_chg":      round(float(row["Pct_Change"]), 3),
        "per1000":      round(float(row["Change_Per1000"]), 2),
        "avg_risk":     round(float(row["Avg_Risk"]), 3),
        "exposure":     round(float(row["Total_Exposure"]), 0),
        "pre_out":      round(float(row["Pre_Output"]), 0),
    })

dashboard_json = {
    "meta": {
        "model": "IMPLAN I-O 2024",
        "baseline": "Pre-AI 2024",
        "scenario": "Post-AI (AV trucking shock)",
        "llm_scenario_assumptions": {
            "NRC-A": -0.08, "NRC-I": -0.05,
            "RC": -0.15, "RM": 0.0, "NRM": 0.0,
            "source": "Acemoglu (2023)"
        },
        "n_industries": len(records),
        "n_sectors": len(sector_records),
    },
    "summary": {
        "current_wave": {
            "total_pre_emp":  6586002,
            "total_post_emp": 6533771,
            "net_jobs":       -52231,
            "pct_change":     -0.7931,
            "labor_income_change_B": -5,
            "output_change_B": 0,
        },
        "llm_wave": {
            "net_jobs": round(df2["LLM_Job_Change"].sum(), 0),
        }
    },
    "sectors":    sector_records,
    "industries": records,
}

with open(f"{OUT}/dashboard.json", "w") as f:
    json.dump(dashboard_json, f, indent=2)

print(f"\n→ output/industry_master.csv  ({len(df2_out)} rows, {len(df2_out.columns)} cols)")
print(f"→ output/sector_summary.csv  ({len(sec_sum)} sectors)")
print(f"→ output/crosstab_sector_alm_employment.csv")
print(f"→ output/crosstab_sector_alm_change.csv")
print(f"→ output/crosstab_sector_cognitive.csv")
print(f"→ output/dashboard.json  ({len(records)} industries, {len(sector_records)} sectors)")
print("\nAll done.")
