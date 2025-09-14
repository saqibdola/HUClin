# -----------------------------
# Configurations
# -----------------------------

# Utility string to append (fixed for all lines)
utility_string = ":80:6 5 13 1 10 3 2 4 9 8 19 0"

# Per-feature utilities (index-based)
feature_utilities = [6, 5, 13, 1, 10, 3, 2, 4, 9, 8, 19, 0]

# Overall utility
overall_utility = 80

# Input and output files
input_file = "heartNo.txt"
output_file_fixed = "NoHUIM.txt"
output_file_utilities = "NoHUIMUSPAN.txt"

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
