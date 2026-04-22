"""
cognitive_classify.py — Adds ALM cognitive task classification to industry data.

Framework: Autor, Levy & Murnane (2003) + Acemoglu & Restrepo (2018) extension.
Five task categories:
  NRC-A  Non-routine Cognitive Analytic     (research, design, software, finance)
  NRC-I  Non-routine Cognitive Interpersonal (management, teaching, sales, law)
  RC     Routine Cognitive                   (clerical, data entry, bookkeeping)
  RM     Routine Manual                      (trucking, assembly, machine operation)
  NRM    Non-routine Manual                  (construction, personal care, food service)

AI Risk Logic (based on Acemoglu & Restrepo 2022 + Felten et al. 2023):
  RM  → HIGH   (current wave: autonomous vehicles, warehouse robots)
  RC  → HIGH   (current wave: LLMs replacing data entry, call centers, back-office)
  NRC-I → MEDIUM (LLMs can draft, but trust/relationship still human)
  NRM → LOW-MED (robotics improving but dexterity still hard)
  NRC-A → LOW-MED (LLMs assist but augment rather than replace at frontier)

Outputs: output/industry_cognitive.csv
"""

import pandas as pd
import re

df = pd.read_csv("output/combined_industry_full.csv")
# Drop the stray header row if present
df = df[df["Industry"] != "Industry Display"].copy()
df["Industry"] = df["Industry"].astype(str).str.strip()

# ── Keyword rules → (category, ai_risk 0-1) ──────────────────────────────────
# Rules applied in order; first match wins.
# ai_risk: 0=very low, 1=very high

rules = [
    # ── NON-ROUTINE MANUAL (NRM) ─────────────────────────────────────────────
    ("NRM", 0.25, [
        "farming", "ranching", "crop", "livestock", "dairy", "poultry", "aquaculture",
        "logging", "fishing", "hunting", "forestry", "nursery", "landscaping",
        "construction", "highway", "street", "building", "residential",
        "masonry", "plumbing", "electrical work", "roofing", "painting",
        "personal care", "laundry", "dry-cleaning", "barber", "nail", "beauty",
        "janitorial", "cleaning", "waste collection", "refuse",
        "home health", "nursing home", "community care",
        "veterinary", "amusement", "gambling", "performing arts",
        "spectator sports", "fitness", "recreation",
        "food service", "restaurant", "drinking", "limited-service", "full-service",
        "hotel", "motel", "accommodation", "rv park", "casino",
        "automotive repair", "car wash",
        "religious", "civic", "social advocacy", "labor union",
        "child day care", "individual and family",
    ]),

    # ── ROUTINE MANUAL (RM) ──────────────────────────────────────────────────
    ("RM", 0.82, [
        "truck", "trucking", "courier", "messenger", "postal",
        "warehousing", "storage",
        "air transportation", "rail", "transit", "pipeline",
        "scenic and sightseeing",
        "manufacturing", "mill", "fabric", "textile", "yarn", "thread",
        "brewery", "winery", "distillery", "tobacco",
        "meat", "poultry processing", "seafood", "bakery", "dairy product",
        "sugar", "confectionery", "fruit", "vegetable preserv",
        "animal food", "flour", "starch", "wet corn",
        "alumin", "steel", "iron", "foundry", "forging", "stamping",
        "machining", "coating", "engraving", "heat treating",
        "plastic", "rubber", "glass", "cement", "concrete", "lime", "gypsum",
        "paper", "paperboard", "pulp",
        "printing", "support activities for printing",
        "petroleum refiner", "asphalt", "lubricant",
        "soap", "cleaning compound", "toilet prep",
        "pharmaceutical", "medicine manufacturing",
        "semiconductor", "electronic component", "audio", "household appliance",
        "motor vehicle", "automobile", "aircraft", "railroad equipment", "ship",
        "engine", "turbine", "boiler", "metalwork", "cutlery", "hardware",
        "mining", "oil and gas extraction", "coal", "quarrying", "drilling",
        "support activities for mining",
        "electric power", "natural gas distribution", "water supply", "sewage",
        "waste management", "remediation",
    ]),

    # ── ROUTINE COGNITIVE (RC) ───────────────────────────────────────────────
    ("RC", 0.78, [
        "insurance carriers", "insurance agency", "insurance fund",
        "data processing", "web hosting", "internet service",
        "accounting", "bookkeeping", "payroll",
        "banking", "credit intermediation", "savings institution",
        "credit card", "consumer lending", "mortgage",
        "securities brokerage", "investment banking", "portfolio management",
        "commodity contracts",
        "real estate agent", "property manager", "appraisal",
        "employment services", "temporary staffing", "professional employer",
        "travel arrangement", "reservation services",
        "telephone", "telecommunications", "satellite",
        "radio", "television broadcasting",
        "cable", "subscription programming",
        "newspaper", "periodical", "book", "directory publisher",
        "investigation", "security service", "armored car",
        "office administrative", "business support",
        "document preparation", "transcription",
        "retail", "wholesale", "gasoline store",
        "warehouse club", "department store", "electronics store",
        "sporting goods", "hobby", "book store",
        "auto dealer", "auto parts",
    ]),

    # ── NON-ROUTINE COGNITIVE INTERPERSONAL (NRC-I) ──────────────────────────
    ("NRC-I", 0.38, [
        "management of companies", "holding",
        "advertising", "public relations", "marketing",
        "education", "elementary school", "secondary school", "junior college",
        "college", "university", "technical school",
        "hospital", "outpatient", "physician", "dentist", "optometrist",
        "chiropractor", "medical laboratory",
        "home health care",
        "social assistance", "vocational rehabilitation",
        "performing arts", "museum", "zoo", "park",
        "grant-making", "advocacy",
        "legal service", "law firm",
        "owner-occupied housing", "tenant-occupied",
        "other real estate",
    ]),

    # ── NON-ROUTINE COGNITIVE ANALYTIC (NRC-A) ───────────────────────────────
    ("NRC-A", 0.28, [
        "software", "computer system", "custom computer", "computer programming",
        "information technology", "systems design",
        "scientific research", "r&d", "research and development",
        "architectural", "engineering service",
        "testing laboratory", "measurement instrument",
        "specialized design",
        "management consulting", "financial advisory",
        "actuarial", "drafting", "surveying", "geophysical",
        "photographic", "translation", "veterinary" ,
        "other financial investment",
    ]),
]

def classify(name: str):
    n = name.lower()
    for cat, risk, keywords in rules:
        if any(k in n for k in keywords):
            return cat, risk
    # Default: unclassified → treat as routine cognitive (mid-risk)
    return "RC", 0.55

df["ALM_Category"], df["AI_Risk_Score"] = zip(*df["Industry"].map(classify))

# Human-readable category label
cat_labels = {
    "NRC-A": "Non-routine Cognitive Analytic",
    "NRC-I": "Non-routine Cognitive Interpersonal",
    "RC":    "Routine Cognitive",
    "RM":    "Routine Manual",
    "NRM":   "Non-routine Manual",
}
df["ALM_Label"] = df["ALM_Category"].map(cat_labels)

# Cognitive flag: is this primarily a "thinking" job?
df["Is_Cognitive"] = df["ALM_Category"].isin(["NRC-A", "NRC-I", "RC"])

df.to_csv("output/industry_cognitive.csv", index=False)

# ── Summary by category ───────────────────────────────────────────────────────
print("=== Classification Summary ===")
summary = df.groupby(["ALM_Category","ALM_Label"]).agg(
    Industries=("Industry","count"),
    Pre_Emp=("Pre_Emp_Total","sum"),
    Post_Emp=("Post_Emp_Total","sum"),
    Job_Change=("Change_Employment","sum"),
    Avg_Risk=("AI_Risk_Score","mean"),
).round(0)
summary["Pct_Change"] = (summary["Job_Change"] / summary["Pre_Emp"] * 100).round(3)
print(summary.to_string())

print("\n=== Cognitive vs Non-cognitive ===")
cog = df.groupby("Is_Cognitive").agg(
    Industries=("Industry","count"),
    Pre_Emp=("Pre_Emp_Total","sum"),
    Job_Change=("Change_Employment","sum"),
).copy()
cog["Pct_Change"] = (cog["Job_Change"] / cog["Pre_Emp"] * 100).round(3)
print(cog.to_string())

print("\n=== Top 10 highest AI-risk industries with most exposure ===")
top = df.nlargest(10,"AI_Risk_Score")[["Industry","ALM_Category","AI_Risk_Score","Pre_Emp_Total","Change_Employment","PctChange_Employment"]]
print(top.to_string())

print("\n→ output/industry_cognitive.csv written.")
