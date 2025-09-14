# -----------------------------
# Configurations
# -----------------------------

# Utility string to append (fixed for all lines)
utility_string = ":376:11 25 6 8 4 9 7 5 1 3 2 12 10 18 28 22 35 14 41 16 31 20 48 0"

# Per-feature utilities (index-based)
feature_utilities = [11, 25, 6, 8, 4, 9, 7, 5, 1, 3, 2, 12, 10, 18, 28, 22, 35, 14, 41, 16, 31, 20, 48, 0]

# Overall utility
overall_utility = 376

# Input and output files
input_file = "CKDYes.txt"
output_file_fixed = "CKDYesHUIM.txt"
output_file_utilities = "CKDYesHUIMUSPAN.txt"

# -----------------------------
# Processing
# -----------------------------
with open(input_file, "r") as infile, \
     open(output_file_fixed, "w") as outfile_fixed, \
     open(output_file_utilities, "w") as outfile_utils:

    for line in infile:
        values = line.strip().split()  # split into feature values

        # --- File 1: original line + fixed utility string ---
        part1 = f"{' '.join(values)}{utility_string}\n"
        outfile_fixed.write(part1)

        # --- File 2: feature values with utilities ---
        part2_parts = []
        for i, val in enumerate(values):
            util = feature_utilities[i]
            part2_parts.append(f"{val}[{util}] -1")
        part2 = " ".join(part2_parts) + f" -2 SUtility:{overall_utility}\n"
        outfile_utils.write(part2)

print("✅ Done! Created two files:\n -", output_file_fixed, "\n -", output_file_utilities)
