"""
fetch_external.py — Pulls BLS OES wages + QCEW state employment using your API key.
Key is read from .env — never hardcoded, never committed.

Run: python3 fetch_external.py
"""

import os, json, time, zipfile, io
import requests
import pandas as pd

# ── Load API key from .env ────────────────────────────────────────────────────
def load_env(path=".env"):
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

env = load_env()
API_KEY = env.get("BLS_API_KEY") or os.environ.get("BLS_API_KEY")

if not API_KEY or API_KEY == "your_key_here":
    print("ERROR: No BLS API key found.")
    print("  1. Go to https://data.bls.gov/registrationEngine/")
    print("  2. Register free — takes 30 seconds")
    print("  3. Paste your key into .env:  BLS_API_KEY=xxxxxxxxxxxxxxxx")
    exit(1)

print(f"API key loaded: {API_KEY[:4]}{'*' * (len(API_KEY)-4)}")

HEADERS = {"Content-type": "application/json"}
OUT = "external"
os.makedirs(OUT, exist_ok=True)

# ── BLS API v2 helper ─────────────────────────────────────────────────────────
def bls_series(series_ids, start_year, end_year, label=""):
    """Fetch multiple series from BLS API v2. Returns DataFrame."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": API_KEY,
        "annualaverage": True,
    }
    r = requests.post(url, json=payload, headers=HEADERS, timeout=30)
    data = r.json()
    if data["status"] != "REQUEST_SUCCEEDED":
        print(f"  BLS API error: {data.get('message', data)}")
        return pd.DataFrame()
    rows = []
    for s in data["Results"]["series"]:
        sid = s["seriesID"]
        for d in s["data"]:
            if d.get("period") == "M13":  # annual average
                rows.append({"series_id": sid, "year": int(d["year"]), "value": float(d["value"].replace(",",""))})
    df = pd.DataFrame(rows)
    if label:
        print(f"  {label}: {len(df)} rows")
    return df

# ── 1. BLS OES — Mean annual wages by major industry sector ──────────────────
# OES series format: OEU{area}{industry}{occupation}{datatype}
# National (area=0000000), all occupations (000000), mean annual wage (03)
# Industry codes: 000000=all, specific NAICS-based codes for sectors
# We'll use cross-industry national series for major sector groups

print("\n── Fetching OES wage data ──")

# Major industry sector series (national, all occupations, mean annual wage)
# Format: OEU0000000 + {6-digit industry} + 000000 + 03
oes_series = {
    "OEU000000000000000003": "All Industries",
    "OEU000000010000000003": "Agriculture",
    "OEU000000021000000003": "Mining",
    "OEU000000022000000003": "Utilities",
    "OEU000000023000000003": "Construction",
    "OEU000000031000000003": "Mfg — Food",
    "OEU000000048000000003": "Transportation & Warehousing",
    "OEU000000051000000003": "Information",
    "OEU000000052000000003": "Finance & Insurance",
    "OEU000000053000000003": "Real Estate",
    "OEU000000054000000003": "Professional Services",
    "OEU000000055000000003": "Management",
    "OEU000000056000000003": "Admin & Support",
    "OEU000000061000000003": "Education",
    "OEU000000062000000003": "Healthcare",
    "OEU000000071000000003": "Arts & Entertainment",
    "OEU000000072000000003": "Hospitality & Food Service",
    "OEU000000081000000003": "Personal Services",
    "OEU000000091000000003": "Government",
}

oes_df = bls_series(list(oes_series.keys()), 2022, 2023, "OES wages")
if not oes_df.empty:
    oes_df["sector"] = oes_df["series_id"].map(oes_series)
    oes_df = oes_df[oes_df["year"] == 2023][["sector","value"]].rename(columns={"value":"mean_annual_wage"})
    oes_df.to_csv(f"{OUT}/oes_wages_by_sector.csv", index=False)
    print(oes_df.to_string(index=False))

# ── 2. BLS QCEW — State-level employment by supersector (2023 annual) ────────
# Series: ENU{state_fips}5{supersector}
# datatype 1 = employment, period M13 = annual average
# Supersectors: 10=goods, 20=natural resources, 30=construction,
#               40=manufacturing, 50=trade/transport, 60=information,
#               70=finance, 80=professional, 90=education/health,
#               A0=leisure, B0=other services, C0=government

print("\n── Fetching QCEW state employment ──")

# Top states by employment for regional map
state_fips = {
    "06": "California", "48": "Texas", "36": "New York",
    "12": "Florida",    "17": "Illinois", "42": "Pennsylvania",
    "39": "Ohio",       "13": "Georgia",  "47": "Tennessee",
    "26": "Michigan",   "37": "North Carolina", "53": "Washington",
}
supersectors = {"10":"Goods Producing","50":"Trade/Transport/Util","60":"Information",
                "70":"Finance","80":"Professional","90":"Edu & Health","C0":"Government"}

qcew_series = []
for fips in list(state_fips.keys())[:8]:   # first 8 states (API limit 50 series/call)
    for ss in list(supersectors.keys())[:5]:
        qcew_series.append(f"ENU{fips}5{ss}")

qcew_df = bls_series(qcew_series, 2022, 2023, "QCEW state employment")
if not qcew_df.empty:
    def parse_qcew(sid):
        fips = sid[3:5]; ss = sid[6:]
        return state_fips.get(fips, fips), supersectors.get(ss, ss)
    qcew_df[["state","supersector"]] = pd.DataFrame(
        qcew_df["series_id"].apply(parse_qcew).tolist(), index=qcew_df.index)
    qcew_df = qcew_df[qcew_df["year"]==2023][["state","supersector","value"]].rename(columns={"value":"employment"})
    qcew_df.to_csv(f"{OUT}/qcew_state_employment.csv", index=False)
    print(f"  Saved {len(qcew_df)} state × sector rows")

# ── 3. O*NET task scores — no API key needed, direct download ────────────────
print("\n── Fetching O*NET task importance scores ──")

onet_url = "https://www.onetcenter.org/dl_files/database/db_29_0_text/Task%20Ratings.txt"
try:
    r = requests.get(onet_url, timeout=30)
    if r.status_code == 200:
        from io import StringIO
        onet_df = pd.read_csv(StringIO(r.text), sep="\t")
        print(f"  O*NET columns: {list(onet_df.columns)}")
        # Keep importance of routine task categories
        onet_relevant = onet_df[onet_df["Scale ID"] == "IM"]  # Importance scale
        onet_relevant.to_csv(f"{OUT}/onet_task_ratings.csv", index=False)
        print(f"  Saved {len(onet_relevant)} task importance rows")
    else:
        print(f"  O*NET HTTP {r.status_code} — will try alternate URL")
        # Alternate: occupation-level automation risk from Frey & Osborne via public CSV
        frey_url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Automation%20risk%20of%20occupations%20(Frey%20%26%20Osborne%2C%202013)/Automation%20risk%20of%20occupations%20(Frey%20%26%20Osborne%2C%202013).csv"
        r2 = requests.get(frey_url, timeout=20)
        if r2.status_code == 200:
            fo_df = pd.read_csv(StringIO(r2.text))
            fo_df.to_csv(f"{OUT}/frey_osborne_automation_risk.csv", index=False)
            print(f"  Saved Frey-Osborne data: {fo_df.shape}")
except Exception as e:
    print(f"  O*NET fetch failed: {e}")

print("\nDone. Check external/ folder.")
