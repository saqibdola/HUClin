import pandas as pd

INPUT_PATH = "2. chronic kidney diseasesNo.xlsx"
OUTPUT_PATH = "CKDNo.txt"

def clean_header(s: str) -> str:
    return str(s).replace("\u00A0", " ").strip()

def norm_str(x):
    if x is None or pd.isna(x):
        return None
    return str(x).strip()

def map_yn(value) -> str:
    v = norm_str(value)
    if v is None: return "0"
    vlow = v.lower()
    if vlow in {"yes","y","1"}: return "1"
    if vlow in {"no","n","0"}:  return "0"
    try:
        f = float(v)
        return "1" if int(f) == 1 else "0"
    except Exception:
        return "0"

def convert_numeric(value, feature_name=None) -> str:
    v = norm_str(value)
    if v is None:
        return "0"

    # 🔹 Special case: preserve #NULL! in these two features
    if v == "#NULL!" and feature_name in {"TriglyceridesBaseline", "HgbA1C"}:
        return "#NULL!"
    if v == ".":
        return "0"

    try:
        f = float(v)
        if f.is_integer():
            return str(int(f))
        s_fmt = f"{f:.1f}"       # one decimal place
        return s_fmt.replace(".", "0")  # e.g., 93.3 -> 933
    except Exception:
        return v.replace(".", "0")

# prefixes for the 24 features (StudyID excluded)
prefix = {
    "Gender": 110, "AgeBaseline": 111, "Age.3.categories": 112,
    "HistoryDiabetes": 113, "HistoryCHD": 114, "HistoryVascular": 115,
    "HistorySmoking": 116, "HistoryHTN": 117, "HistoryDLD": 118,
    "HistoryObesity": 119, "DLDmeds": 120, "DMmeds": 121, "HTNmeds": 122,
    "ACEIARB": 123, "CholesterolBaseline": 124, "TriglyceridesBaseline": 125,
    "HgbA1C": 126, "CreatnineBaseline": 127, "eGFRBaseline": 128,
    "sBPBaseline": 129, "dBPBaseline": 130, "BMIBaseline": 131,
    "TimeToEventMonths": 132, "EventCKD35": 133
}

# Load as strings so "#NULL!" is preserved
df = pd.read_excel(INPUT_PATH, dtype=str)
df.columns = [clean_header(c) for c in df.columns]
if "StudyID" in df.columns:
    df = df.drop(columns=["StudyID"])

# 🔹 Remove rows that contain any NaN/missing value
rows_before = len(df)
df = df.dropna()
rows_after = len(df)
print(f"Removed {rows_before - rows_after} rows with missing/NaN values.")

required = list(prefix.keys())
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing expected columns: {missing}")

bin_cols_without_event = [
    "HistoryDiabetes","HistoryCHD","HistoryVascular","HistorySmoking","HistoryHTN",
    "HistoryDLD","HistoryObesity","DLDmeds","DMmeds","HTNmeds","ACEIARB"
]
num_cols = [
    "CholesterolBaseline","TriglyceridesBaseline","HgbA1C","CreatnineBaseline",
    "eGFRBaseline","sBPBaseline","dBPBaseline","BMIBaseline","TimeToEventMonths"
]
event_col = "EventCKD35"

converted_strings = []
for _, row in df.iterrows():
    parts = []

    # Gender
    g = norm_str(row.get("Gender"))
    if g and g.lower() in {"male","m","1"}:
        gv = "1"
    elif g and g.lower() in {"female","f","0"}:
        gv = "0"
    else:
        gv = "0"
    parts.append(f"{prefix['Gender']}{gv}")

    # AgeBaseline
    parts.append(f"{prefix['AgeBaseline']}{convert_numeric(row.get('AgeBaseline'))}")

    # Age.3.categories
    a3 = norm_str(row.get("Age.3.categories"))
    mapping = {
        "< 50":"0","<50":"0","less than 50":"0","lt50":"0",
        "age > 51 < 65":"1","> 51 < 65":"1",">51 & <65":"1","51-65":"1",
        "> 65":"2",">65":"2","over 65":"2","gt65":"2",
        "0":"0","1":"1","2":"2"
    }
    av = mapping.get(a3.lower() if a3 else "0", "0")
    parts.append(f"{prefix['Age.3.categories']}{av}")

    # Binary features
    for c in bin_cols_without_event:
        parts.append(f"{prefix[c]}{map_yn(row.get(c))}")

    # Numeric features (special case for TriglyceridesBaseline, HgbA1C)
    for c in num_cols:
        parts.append(f"{prefix[c]}{convert_numeric(row.get(c), feature_name=c)}")

    # EventCKD35 last
    parts.append(f"{prefix[event_col]}{map_yn(row.get(event_col))}")

    converted_strings.append(" ".join(parts))

# Save TXT
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.writelines(line + "\n" for line in converted_strings)

print(f"✅ Done! Saved {len(converted_strings)} rows to {OUTPUT_PATH}")
