# -----------------------------
# Configurations
# -----------------------------

# Utility string to append (fixed for all lines)
utility_string = ":177:27 21 32 9 5 13 10 12 6 17 4 0 1 8 2 3 7"

# Per-feature utilities (index-based)
feature_utilities = [27, 21, 32, 9, 5, 13, 10, 12, 6, 17, 4, 0, 1, 8, 2, 3, 7]
   # 21, 32, 27, 17, 13, 5, 6, 4, 2, 12, 3, 0, 1, 7, 8, 10, 9]

# Overall utility
overall_utility = 177

# Input and output
# iles
input_file = "CDCLCC.txt"
output_file_fixed = "CDCLCCCHUIM.txt"
output_file_utilities = "CDCLCCCHUIMUSPAN.txt"

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
