import pandas as pd

# Load dataset
df = pd.read_csv("heartNo.csv")

# Mapping rules
sex_map = {"M": 1, "F": 0}
chest_pain_map = {"ATA": 1, "NAP": 2, "ASY": 3, "TA": 4}
resting_ecg_map = {"Normal": 1, "ST": 2, "LVH": 3}
exercise_angina_map = {"Y": 1, "N": 0}
st_slope_map = {"Up": 1, "Flat": 2, "Down": 3}

# Prefixes
prefixes = {
    "Age": 888,
    "Sex": 889,
    "ChestPainType": 890,
    "RestingBP": 891,
    "Cholesterol": 892,
    "FastingBS": 893,
    "RestingECG": 894,
    "MaxHR": 895,
    "ExerciseAngina": 896,
    "Oldpeak": 897,
    "ST_Slope": 898,
    "HeartDisease": 899
}

converted_rows = []

for _, row in df.iterrows():
    parts = []

    # Age
    parts.append(f"{prefixes['Age']}{row['Age']}")

    # Sex
    sex_val = sex_map.get(row['Sex'], row['Sex'])
    parts.append(f"{prefixes['Sex']}{sex_val}")

    # ChestPainType
    cp_val = chest_pain_map.get(row['ChestPainType'], row['ChestPainType'])
    parts.append(f"{prefixes['ChestPainType']}{cp_val}")

    # RestingBP
    parts.append(f"{prefixes['RestingBP']}{row['RestingBP']}")

    # Cholesterol
    parts.append(f"{prefixes['Cholesterol']}{row['Cholesterol']}")

    # FastingBS
    parts.append(f"{prefixes['FastingBS']}{row['FastingBS']}")

    # RestingECG
    ecg_val = resting_ecg_map.get(row['RestingECG'], row['RestingECG'])
    parts.append(f"{prefixes['RestingECG']}{ecg_val}")

    # MaxHR
    parts.append(f"{prefixes['MaxHR']}{row['MaxHR']}")

    # ExerciseAngina
    angina_val = exercise_angina_map.get(row['ExerciseAngina'], row['ExerciseAngina'])
    parts.append(f"{prefixes['ExerciseAngina']}{angina_val}")

    # Oldpeak (handle negatives + format)
    oldpeak_val = row['Oldpeak']

    if isinstance(oldpeak_val, (int, float)) and oldpeak_val < 0:
        oldpeak_val = "999"
    elif str(oldpeak_val).strip() == ".":
        oldpeak_val = "0"
    elif isinstance(oldpeak_val, float) and oldpeak_val.is_integer():
        oldpeak_val = str(int(oldpeak_val))
    else:
        oldpeak_val = str(oldpeak_val).replace(".", "0")

    parts.append(f"{prefixes['Oldpeak']}{oldpeak_val}")

    # ST_Slope
    slope_val = st_slope_map.get(row['ST_Slope'], row['ST_Slope'])
    parts.append(f"{prefixes['ST_Slope']}{slope_val}")

    # HeartDisease
    parts.append(f"{prefixes['HeartDisease']}{row['HeartDisease']}")

    converted_rows.append(" ".join(map(str, parts)))

# Save output
output_file = "heartNo.txt"
with open(output_file, "w") as f:
    for line in converted_rows:
        f.write(line + "\n")

print("✅ Conversion complete! Saved to", output_file)
