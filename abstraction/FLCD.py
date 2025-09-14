#!/usr/bin/env python3
"""
CSV transformer with custom dot handling:
- If value starts with '0.' -> remove the FIRST dot only (e.g., 0.626 -> 0626)
- Else -> replace ALL '.' with '0' (e.g., 1.441 -> 10441)
- Prepend auto IDs per column: 11, 22, 33, ...
- Output: <base>Yes.txt (tab-delimited) WITHOUT header row
"""

import os
import sys
import pandas as pd

# ---- set your CSV file name here ----
IN_PATH = "FLCDYes.csv"
# -------------------------------------

def assign_ids(columns):
    """Assign sequential IDs: 11, 22, 33, ..."""
    return {col: (i + 1) * 11 for i, col in enumerate(columns)}


def transform_token(s: str) -> str:
    """Transform numbers:
       - If integer (no '.'): leave unchanged
       - If decimal:
           * Replace '.' with '0'
           * Keep only first 2 digits after '.'
           * Drop the leading 0 if the number is <1
       Examples:
         1.456743 -> 1045
         0.626    -> 062
         0.05     -> 005
         12.3     -> 1203
         55       -> 55
    """
    if s is None:
        return ""
    s = str(s).strip()
    if s == "":
        return ""

    if "." in s:
        before, after = s.split(".", 1)
        after = after[:2]  # take only first 2 digits
        transformed = before + "0" + after
        # Drop leading zero if original number was <1 (like 0.xxx)
        if before == "0":
            transformed = transformed[1:]
        return transformed
    else:
        return s

def transform_dataframe(df: pd.DataFrame, col_id_map: dict) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for col in df.columns:
        col_id = str(col_id_map[col])
        out[col] = df[col].map(
            lambda v: "" if (v is None or str(v).strip() == "") else col_id + transform_token(str(v))
        )
    return out

def main():
    in_path = IN_PATH
    if not os.path.isfile(in_path):
        print(f"Input file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(in_path, dtype=str, keep_default_na=False, na_filter=False)
    except Exception as e:
        print(f"Failed to read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    id_map = assign_ids(df.columns)
    print("Assigned IDs:", id_map)

    try:
        df_out = transform_dataframe(df, id_map)
    except Exception as e:
        print(f"Transformation failed: {e}", file=sys.stderr)
        sys.exit(1)

    base, _ = os.path.splitext(in_path)
    out_txt  = f"{base}.txt"

    try:
        # Write without header row
        df_out.to_csv(out_txt, sep="\t", index=False, header=False, encoding="utf-8", lineterminator="\n")
    except Exception as e:
        print(f"Failed to write outputs: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Wrote: {out_txt}")

if __name__ == "__main__":
    main()
