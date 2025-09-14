import pandas as pd
import re

# ---- Paths ----
INPUT_PATH = "Disease_symptom_and_patient_profile_datasetPositive.csv"  # adjust if needed
OUTPUT_PATH = "DSPPPositive.txt"

# ---- Header normalization helper ----
def norm_key(s: str) -> str:
    return re.sub(r"[^0-9a-z]", "", str(s).lower())

# Expected canonical headers
expected = [
    "Disease","Fever","Cough","Fatigue","Difficulty Breathing",
    "Age","Gender","Blood Pressure","Cholesterol Level","Outcome Variable",
]
expected_norm = {c: norm_key(c) for c in expected}

# ---- Load CSV as strings (robust to mixed content) ----
df = pd.read_csv(INPUT_PATH, dtype=str)
orig_cols = list(df.columns)
norm_lookup = {norm_key(c): c for c in orig_cols}

# Map canonical -> actual column names
col_map, missing = {}, []
for c in expected:
    nk = expected_norm[c]
    if nk in norm_lookup:
        col_map[c] = norm_lookup[nk]
    else:
        missing.append(c)

# Require at least Disease and Outcome
for crit in ["Disease", "Outcome Variable"]:
    if crit not in col_map:
        raise ValueError(f"Critical column missing: {crit}. Found columns: {orig_cols}")

# ---- Mappings ----
disease_map_list = [
 ("Influenza",1),("Common cold",2),("Eczema",3),("Asthma",4),("Hyperthyroidism",5),
 ("Allergic Rhinitis",6),("Anxiety Disorders",7),("Diabetes",8),("Gastroenteritis",9),
 ("Pancreatitis",10),("Rheumatoid Arthritis",11),("Depression",12),("Liver Cancer",13),
 ("Stroke",14),("Urinary Tract Infection",15),("Dengue Fever",16),("Hepatitis",17),
 ("Kidney Cancer",18),("Migraine",19),("Muscular Dystrophy",20),("Sinusitis",21),
 ("Ulcerative Colitis",22),("Bipolar Disorder",23),("Bronchitis",24),("Cerebral Palsy",25),
 ("Colorectal Cancer",26),("Hypertensive Heart Disease",27),("Multiple Sclerosis",28),
 ("Myocardial Infarction",29),("15 (UTI)",30),("Osteoporosis",31),("Pneumonia",32),
 ("Atherosclerosis",33),("Chronic Obstructive Pulmonary Disease (COPD)",34),("Epilepsy",35),
 ("Hypertension",36),("Obsessive-Compulsive Disorder",37),("Psoriasis",38),("Rubella",39),
 ("Cirrhosis",40),("Conjunctivitis (Pink Eye)",41),("Liver Disease",42),("Malaria",43),
 ("Spina Bifida",44),("Kidney Disease",45),("Osteoarthritis",46),("Klinefelter Syndrome",47),
 ("Acne",48),("Brain Tumor",49),("Cystic Fibrosis",50),("Glaucoma",51),("Rabies",52),
 ("Chickenpox",53),("Coronary Artery Disease",54),("Eating Disorders",55),("Fibromyalgia",56),
 ("Hemophilia",57),("Hypoglycemia",58),("Lymphoma",59),("Tuberculosis",60),("Lung Cancer",61),
 ("Hypothyroidism",62),("Autism Spectrum Disorder (ASD)",63),("Crohn's Disease",64),
 ("Hyperglycemia",65),("Melanoma",66),("Ovarian Cancer",67),("Turner Syndrome",68),
 ("Zika Virus",69),("Cataracts",70),("Pneumocystis 32 (PCP)",71),("Scoliosis",72),
 ("Sickle Cell Anemia",73),("Tetanus",74),("Anemia",75),("Cholera",76),("Endometriosis",77),
 ("Sepsis",78),("Sleep Apnea",79),("Down Syndrome",80),("Ebola Virus",81),("Lyme Disease",82),
 ("Pancreatic Cancer",83),("Pneumothorax",84),("Appendicitis",85),("Esophageal Cancer",86),
 ("HIV/AIDS",87),("Marfan Syndrome",88),("Parkinson's Disease",89),("Hemorrhoids",90),
 ("Polycystic Ovary Syndrome (PCOS)",91),("Systemic Lupus Erythematosus",92),("Typhoid Fever",93),
 ("Breast Cancer",94),("Measles",95),("Osteomyelitis",96),("Polio",97),("Chronic 45",98),
 ("17 B",99),("Prader-Willi Syndrome",100),("Thyroid Cancer",101),("Bladder Cancer",102),
 ("Otitis Media (Ear Infection)",103),("Tourette Syndrome",104),("Alzheimer's Disease",105),
 ("Dementia",106),("Diverticulitis",107),("Mumps",108),("Cholecystitis",109),("Prostate Cancer",110),
 ("Schizophrenia",111),("Gout",112),("Testicular Cancer",113),("Tonsillitis",114),
 ("Williams Syndrome",115)
]
disease_map = {name.lower().strip(): code for name, code in disease_map_list}

yn_map      = {"yes":1, "y":1, "1":1, "no":0, "n":0, "0":0}
gender_map  = {"male":1, "m":1, "female":0, "f":0, "0":0, "1":1}
bp_map      = {"normal":0, "high":1, "low":2}
chol_map    = {"normal":0, "high":1, "low":2}  # <- categorical per your correction
outcome_map = {"positive":1, "1":1, "negative":0, "0":0}

def to_int_str(v):
    """Coerce to integer string; empty/NaN -> '0'."""
    if v is None:
        return "0"
    s = str(v).strip()
    if s == "":
        return "0"
    try:
        return str(int(float(s)))
    except Exception:
        return "0"

# ---- Build output ----
converted = []
for _, row in df.iterrows():
    parts = []

    # 1) Disease
    raw = str(row[col_map["Disease"]]).strip() if "Disease" in col_map and pd.notna(row[col_map["Disease"]]) else ""
    parts.append(f"1{disease_map.get(raw.lower(), 0)}")

    # 2) Fever
    raw = str(row[col_map["Fever"]]).strip() if "Fever" in col_map and pd.notna(row[col_map["Fever"]]) else ""
    parts.append(f"2{yn_map.get(raw.lower(), 0)}")

    # 3) Cough
    raw = str(row[col_map["Cough"]]).strip() if "Cough" in col_map and pd.notna(row[col_map["Cough"]]) else ""
    parts.append(f"3{yn_map.get(raw.lower(), 0)}")

    # 4) Fatigue
    raw = str(row[col_map["Fatigue"]]).strip() if "Fatigue" in col_map and pd.notna(row[col_map["Fatigue"]]) else ""
    parts.append(f"4{yn_map.get(raw.lower(), 0)}")

    # 5) Difficulty Breathing
    raw = str(row[col_map["Difficulty Breathing"]]).strip() if "Difficulty Breathing" in col_map and pd.notna(row[col_map["Difficulty Breathing"]]) else ""
    parts.append(f"5{yn_map.get(raw.lower(), 0)}")

    # 6) Age (integer)
    raw = row[col_map["Age"]] if "Age" in col_map else None
    parts.append(f"6{to_int_str(raw)}")

    # 7) Gender
    raw = str(row[col_map["Gender"]]).strip() if "Gender" in col_map and pd.notna(row[col_map["Gender"]]) else ""
    parts.append(f"7{gender_map.get(raw.lower(), 0)}")

    # 8) Blood Pressure
    raw = str(row[col_map["Blood Pressure"]]).strip() if "Blood Pressure" in col_map and pd.notna(row[col_map["Blood Pressure"]]) else ""
    parts.append(f"8{bp_map.get(raw.lower(), 0)}")

    # 9) Cholesterol Level (categorical)
    raw = str(row[col_map["Cholesterol Level"]]).strip() if "Cholesterol Level" in col_map and pd.notna(row[col_map["Cholesterol Level"]]) else ""
    parts.append(f"9{chol_map.get(raw.lower(), 0)}")

    # 991) Outcome Variable
    raw = str(row[col_map["Outcome Variable"]]).strip() if "Outcome Variable" in col_map and pd.notna(row[col_map["Outcome Variable"]]) else ""
    parts.append(f"991{outcome_map.get(raw.lower(), 0)}")

    converted.append(" ".join(parts))

# ---- Save TXT ----
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for line in converted:
        f.write(line + "\n")

print(f"✅ Done! Saved {len(converted)} rows to {OUTPUT_PATH}")
