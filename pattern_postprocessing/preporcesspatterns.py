#!/usr/bin/env python3
"""
Preprocess all .txt files in a folder (paths hardcoded in the script).

Rules:
- Remove tags like "#UTIL:" or "#BOND:" AND the value that follows them.
- Remove negative integers and any non-integer tokens.
- Keep only positive integers (> 0).
- Drop a line if it has fewer than 3 positive integers.
- Write at most N lines per file (default: 500).
- If an output file has fewer than N lines, print a warning.
"""

import re
from pathlib import Path
from typing import List

# <<< EDIT THESE PATHS >>
INPUT_FOLDER = Path("DSPPU1patterns")       # folder containing your input .txt files
OUTPUT_FOLDER = Path("DSPPpatternsU1Cleaned") # folder where cleaned files will be saved
MAX_LINES = 500


TAG_PATTERN = re.compile(r'^#\w+:$')          # e.g., #UTIL:  #BOND:
INT_PATTERN = re.compile(r'^[+-]?\d+$')       # integer tokens


def clean_line(line: str) -> List[str]:
    """Clean one line and return the list of positive integers kept."""
    tokens = line.strip().split()
    cleaned: List[str] = []
    skip_next = False

    for tok in tokens:
        if skip_next:
            skip_next = False
            continue

        if TAG_PATTERN.match(tok):
            skip_next = True  # skip tag value
            continue

        if INT_PATTERN.match(tok):
            try:
                val = int(tok)
            except ValueError:
                continue
            if val > 0:
                cleaned.append(str(val))

    return cleaned


def process_file(input_path: Path, output_path: Path, max_lines: int = 500) -> int:
    """Process one file and return the number of lines written."""
    written = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open('r', encoding='utf-8', errors='ignore') as fin, \
         output_path.open('w', encoding='utf-8') as fout:
        for raw in fin:
            ints = clean_line(raw)
            if len(ints) >= 3:
                fout.write(' '.join(ints) + '\n')
                written += 1
                if written >= max_lines:
                    break
    return written


def main():
    if not INPUT_FOLDER.exists() or not INPUT_FOLDER.is_dir():
        raise SystemExit(f"Input folder not found: {INPUT_FOLDER}")

    txt_files = list(INPUT_FOLDER.glob("*.txt"))
    if not txt_files:
        raise SystemExit(f"No .txt files found in {INPUT_FOLDER}")

    for file in txt_files:
        out_file = OUTPUT_FOLDER / f"{file.stem}_cleaned.txt"
        written = process_file(file, out_file, max_lines=MAX_LINES)
        print(f"Processed {file.name} -> {out_file.name} ({written} lines)")

        # Check if fewer than MAX_LINES
        if written < MAX_LINES:
            print(f"⚠️  Warning: {out_file.name} has only {written} lines (less than {MAX_LINES}).")


if __name__ == "__main__":
    main()
