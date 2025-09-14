import os
import re
import sys
import pandas as pd

# -------------------- CONFIG --------------------
INPUT_PATH = "diabetesYes.csv"        # <-- set to your diabetes dataset
OUTPUT_PATH = "DiabetisYes.txt"  # output text file

# If you want to also drop a leading '0' after handling '0.' in DiabetesPedigreeFunction, set True
DROP_LEADING_ZERO_IN_DPF = False

# -------------------- LABEL/PREFIX MAP --------------------
PREFIX = {
    "pregnancies": "111",
    "glucose": "222",
    "bloodpressure": "333",
    "skinthickness": "444",
    "insulin": "555",
    "bmi": "66",
    "diabetespedigreefunction": "77",
    "age": "888",
    "outcome": "9999",
}

# -------------------- HELPERS --------------------
def norm_key(s: str) -> str:
    """Lowercase, remove non-alphanumerics (to match columns robustly)."""
    return re.sub(r"[^0-9a-z]", "", str(s).lower())

def transform_bmi(v) -> str:
    """
    BMI: replace '.' with '0'
    e.g., '31.6' -> '316' with '0'? No, we *replace* '.' with '0' => '31' + '0' + '6' = '3106'
    Keep all other characters (digits) as-is.
    """
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return s.replace(".", "0")

def transform_dpf(v) -> str:
    """
    DiabetesPedigreeFunction:
      - replace '.' with '0', EXCEPT when the dot follows a leading '0.' — in that case remove the dot.
      Examples:
        '1.441'  -> '10441'
        '0.626'  -> '0626'  (dot removed, not replaced with 0)
      If DROP_LEADING_ZERO_IN_DPF is True, '0.626' -> '626'.
    """
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()

    # Special-case a leading "0."
    if s.startswith("0."):
        # remove ONLY that first dot
        s = "0" + s[2:]  # turns '0.626' into '0626'
        if DROP_LEADING_ZERO_IN_DPF and s.startswith("0") and len(s) > 1:
            s = s[1:]  # drop the leading zero if configured
        return s

    # Otherwise, replace all dots with '0'
    return s.replace(".", "0")

def passthrough_num(v) -> str:
    """Keep numeric-looking values as-is (strip whitespace). Empty/NaN -> ''."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()

# -------------------- LOAD --------------------
if not os.path.exists(INPUT_PATH):
    print(f"❌ Input file not found: {os.path.abspath(INPUT_PATH)}")
    sys.exit(1)

df = None
for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
    try:
        df = pd.read_csv(INPUT_PATH, dtype=str, encoding=enc)
        print(f"• Loaded CSV with encoding: {enc}")
        break
    except Exception as e:
        print(f"• Failed encoding {enc}: {e}")

if df is None:
    print("❌ Could not read the CSV with common encodings.")
    sys.exit(1)

# -------------------- COLUMN RESOLUTION --------------------
# Map your expected fields to actual dataframe columns by normalized key
norm_cols = {col: norm_key(col) for col in df.columns}
rev = {}
for raw, nk in norm_cols.items():
    rev.setdefault(nk, raw)

def col(name):
    nk = norm_key(name)
    return rev.get(nk)

required = [
    "Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin",
    "BMI","DiabetesPedigreeFunction","Age","Outcome"
]
missing = [c for c in required if col(c) is None]
if missing:
    print("❌ Missing expected columns:", ", ".join(missing))
    print("Columns found:", list(df.columns))
    sys.exit(1)

# -------------------- BUILD LINES --------------------
lines = []
for _, row in df.iterrows():
    parts = []

    # Pregnancies (prefix 111)
    parts.append(PREFIX["pregnancies"] + passthrough_num(row[col("Pregnancies")]))

    # Glucose (222)
    parts.append(PREFIX["glucose"] + passthrough_num(row[col("Glucose")]))

    # BloodPressure (333)
    parts.append(PREFIX["bloodpressure"] + passthrough_num(row[col("BloodPressure")]))

    # SkinThickness (444)
    parts.append(PREFIX["skinthickness"] + passthrough_num(row[col("SkinThickness")]))

    # Insulin (555)
    parts.append(PREFIX["insulin"] + passthrough_num(row[col("Insulin")]))

    # BMI (66) – replace '.' with '0'
    parts.append(PREFIX["bmi"] + transform_bmi(row[col("BMI")]))

    # DiabetesPedigreeFunction (77) – special dot rules
    parts.append(PREFIX["diabetespedigreefunction"] + transform_dpf(row[col("DiabetesPedigreeFunction")]))

    # Age (888)
    parts.append(PREFIX["age"] + passthrough_num(row[col("Age")]))

    # Outcome (9999)
    parts.append(PREFIX["outcome"] + passthrough_num(row[col("Outcome")]))

    lines.append(" ".join(parts))

# -------------------- SAVE --------------------
out_path = os.path.abspath(OUTPUT_PATH)
os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Wrote {len(lines)} rows to {out_path}")
