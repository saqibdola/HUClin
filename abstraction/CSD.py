import os
import sys
import re
import pandas as pd

# -------------------- Paths --------------------
# -------------------- Paths --------------------
INPUT_PATH = "8. MC CDC_DataLCC.csv"   # <-- change if needed
OUTPUT_PATH = "CDCLCC.txt"                   # relative or absolute path is fine

# -------------------- Helpers --------------------
def norm_key(s: str) -> str:
    """Normalize header names to alphanumeric lowercase (removes spaces, ?, etc.)."""
    return re.sub(r"[^0-9a-z]", "", str(s).lower())

def norm_val(s: str) -> str:
    """Normalize cell values for mapping (lowercase, trim, dash normalize, collapse spaces)."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s = str(s).strip().lower()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    return s

def to_int_str(v) -> str:
    """Coerce to integer-like string; blanks/NaN -> '0'."""
    if v is None:
        return "0"
    s = str(v).strip()
    if s == "" or s.lower() in {"nan", "none"}:
        return "0"
    try:
        return str(int(float(s)))
    except Exception:
        return "0"

def age_to_code(v) -> int:
    """Map many age-group variants (and digits) to 1..4; unknown/missing -> 0."""
    if v is None:
        return 0
    s = str(v).strip().lower()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    s = s.replace("yrs", "years")

    # Already coded 1..4
    if re.fullmatch(r"[1-4]", s):
        return int(s)

    # Canonical unknowns
    if s in {"", "unknown", "missing", "na", "n/a", "none"}:
        return 0

    # Exact ranges
    m = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        low = int(m.group(1)); high = int(m.group(2))
        if low == 0 and high == 17: return 1
        if low == 18 and high == 49: return 2
        if low == 50 and high == 64: return 3

    # 65+ variants
    if re.search(r"\b65\s*\+|\b65\s*years?\s*(and|or)?\s*older\b", s):
        return 4

    # Heuristic: single age present
    m = re.search(r"\b(\d{1,3})\b", s)
    if m:
        n = int(m.group(1))
        if 0 <= n <= 17:  return 1
        if 18 <= n <= 49: return 2
        if 50 <= n <= 64: return 3
        if n >= 65:       return 4

    return 0

def coded_lookup(mapper, v, default=0):
    """Accept already-coded integers; else normalize and map."""
    s = norm_val(v)
    if re.fullmatch(r"\d+", s):
        try:
            return int(s)
        except Exception:
            return default
    return mapper.get(s, default)

# -------------------- Categorical mappings --------------------
sex_map = {"male":1, "m":1, "female":0, "f":0, "unknown":2, "missing":2, "other":2}
race_map = {
    "unknown":0, "white":1, "multiple":2, "other":2, "multiple/other":2,
    "black":3, "black or african american":3, "african american":3,
    "asian":4,
    "american indian/alaska native":5, "ai/an":5,
    "native hawaiian/other pacific islander":6, "nh/opi":6
}
eth_map = {
    "hispanic":0, "latino":0, "hispanic/latino":0,
    "non-hispanic":1, "not h i s p a n i c or latino".replace(" ", ""):1,  # safeguard
    "not hispanic or latino":1, "nonhispanic":1,
    "unknown":2, "missing":2
}
process_map = {
    "unknown":0, "contact tracing of case patient":1, "contact tracing":1,
    "multiple":2, "routine surveillance":3, "laboratory reported":4,
    "clinical evaluation":5, "other":6, "provider reported":7,
    "other detection method (specify)":8, "routine physical examination":9
}
exposure_map = {"yes":1, "y":1, "true":1, "unknown":0, "no":0, "n":0, "false":0, "missing":0}
status_map = {
    "laboratory-confirmed case":0, "laboratory confirmed case":0, "confirmed":0,
    "probable case":1, "probable":1
}
symptom_map = {"asymptomatic":0, "symptomatic":1, "unknown":2, "missing":3}
yn_unknown_map = {"yes":1, "y":1, "true":1, "no":0, "n":0, "false":0, "unknown":2, "missing":2}
underlying_map = {"yes":1, "y":1, "true":1, "no":0, "n":0, "false":0}

# -------------------- Feature aliases (normalized header -> std key) --------------------
ALIASES = {
    # raw (no prefix)
    "casemonth": "case_month",
    "statefipscode": "state_fips_code",
    "countyfipscode": "county_fips_code",

    # age (1–4, no prefix)
    "agegroup": "age_group",

    # coded (with prefixes)
    "sex": "sex", "race": "race", "ethnicity": "ethnicity",
    "casepositivespecimeninterval": "case_positive_specimen_interval",
    "caseonsetinterval": "case_onset_interval",
    "process": "process",
    "exposure": "exposure", "exposureyn": "exposure",
    "currentstatus": "current_status",
    "symptomstatus": "symptom_status",
    "hospital": "hospital", "hospyn": "hospital",
    "icu": "icu", "icuyn": "icu",
    "death": "death", "deathyn": "death", "deceased": "death",
    "underlyingconditions": "underlying_conditions", "underlyingconditionsyn": "underlying_conditions",
}

# std key -> (type, prefix (if coded), mapper)
FEATURE_INFO = {
    "case_month": ("raw",   "",    None),
    "state_fips_code": ("raw", "", None),
    "county_fips_code": ("raw", "", None),
    "age_group": ("age", "", None),

    "sex": ("coded", "9991", sex_map),
    "race": ("coded", "9992", race_map),
    "ethnicity": ("coded", "9993", eth_map),
    "case_positive_specimen_interval": ("coded", "9994", None),  # numeric
    "case_onset_interval":            ("coded", "9995", None),   # numeric
    "process": ("coded", "9996", process_map),
    "exposure": ("coded", "9997", exposure_map),
    "current_status": ("coded", "9998", status_map),
    "symptom_status": ("coded", "9999", symptom_map),
    "hospital": ("coded", "9889", yn_unknown_map),
    "icu":      ("coded", "9888", yn_unknown_map),
    "death":    ("coded", "9887", yn_unknown_map),
    "underlying_conditions": ("coded", "9886", underlying_map),
}

def fail(msg: str):
    print(f"❌ {msg}")
    sys.exit(1)

def info(msg: str):
    print(f"• {msg}")

# -------------------- Validate input path --------------------
abs_in = os.path.abspath(INPUT_PATH)
info(f"Looking for input CSV at: {abs_in}")
if not os.path.exists(INPUT_PATH):
    fail("Input file not found. Check INPUT_PATH.")

# -------------------- Load CSV (encoding fallback) --------------------
df = None
for enc in ("utf-8-sig", "latin1", "cp1252"):
    try:
        df = pd.read_csv(INPUT_PATH, dtype=str, low_memory=False, encoding=enc)
        info(f"Loaded CSV with encoding: {enc}")
        break
    except Exception as e:
        info(f"Encoding {enc} failed: {e}")
if df is None:
    fail("Could not read the CSV with utf-8-sig/latin1/cp1252.")

rows, cols = df.shape
info(f"DataFrame shape: {rows} rows x {cols} columns")
if rows == 0:
    info("Warning: CSV has 0 rows. An empty output file will still be created.")

# -------------------- Drop redundant columns --------------------
drop_before = set(df.columns)
for redundant in ["res_state", "res_county", "res_county "]:
    if redundant in df.columns:
        df = df.drop(columns=[redundant])
dropped = drop_before - set(df.columns)
if dropped:
    info(f"Dropped redundant columns: {sorted(dropped)}")

# -------------------- Inspect & map columns --------------------
norm_cols = {col: norm_key(col) for col in df.columns}
mapped_cols = {col: ALIASES.get(nk) for col, nk in norm_cols.items() if ALIASES.get(nk)}
unmapped_cols = [col for col in df.columns if col not in mapped_cols]

info(f"Mapped columns count: {len(mapped_cols)}")
if len(mapped_cols) == 0:
    info("No columns matched expected aliases. Check your CSV headers.")
    info("Here are your headers (and their normalized form):")
    for col, nk in norm_cols.items():
        print(f"  - '{col}'  ->  '{nk}'")
    # We'll still write an empty file to make behavior explicit.

# -------------------- Build output following INPUT COLUMN ORDER --------------------
lines = []
cols_in_order = list(df.columns)  # preserve exact file order

for r_idx, (_, row) in enumerate(df.iterrows(), start=1):
    parts = []
    for raw_col in cols_in_order:
        nk = norm_key(raw_col)

        # Skip redundant (normalized)
        if nk in {"resstate", "rescounty"}:
            continue

        std = ALIASES.get(nk)
        if not std:
            continue

        ftype, prefix, mapper = FEATURE_INFO[std]
        val = row.get(raw_col, None)

        if ftype == "raw":
            if std == "case_month":
                parts.append("" if val is None else str(val).replace("-", "").strip())
            else:
                parts.append("" if val is None else str(val).strip())

        elif ftype == "age":
            parts.append(str(age_to_code(val)))  # 1–4 (or 0)

        elif ftype == "coded":
            if std in {"case_positive_specimen_interval", "case_onset_interval"}:
                try:
                    num = int(float(val))
                except Exception:
                    num = 0
                if num < 0:
                    num = 0
                parts.append(prefix + str(num))
            else:
                mapped_int = coded_lookup(mapper, val, 0)
                parts.append(prefix + str(mapped_int))

    lines.append(" ".join(parts))

info(f"Built {len(lines)} output lines.")

# -------------------- Save --------------------
abs_out = os.path.abspath(OUTPUT_PATH)
out_dir = os.path.dirname(abs_out)
if out_dir and not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)

try:
    with open(abs_out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
except Exception as e:
    fail(f"Could not write output file: {e}")

# Verify
if os.path.exists(abs_out):
    size = os.path.getsize(abs_out)
    info(f"✅ Wrote {len(lines)} rows to: {abs_out}  ({size} bytes)")
else:
    fail("Write completed without error but file not found (unexpected).")
