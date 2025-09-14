#!/usr/bin/env python3
"""
Preprocess all .txt files in a folder (paths hardcoded in the script), with pair normalization.

Pipeline per file:
1) Clean each line:
   - Remove tags like "#UTIL:" or "#BOND:" AND the *next* value.
   - Remove negative integers and non-integer tokens.
   - Keep only positive integers (> 0).
   - Drop line if it has fewer than 3 positive integers.
2) Keep at most MAX_LINES lines, preserving order.
3) For Yes/No pairs that share the same base name (e.g., EFIMYes & EFIMNo),
   find the **maximum count of integers per line across the pair**.
4) For each kept line:
   - Join integers with commas (no spaces).
   - Pad with '?' (comma-separated) to match the pair's maximum length.
5) Write the result and:
   - Warn if fewer than MAX_LINES lines were written.
   - Print both total lines written and the (normalized) maximum line length.
   - Print a normalization note when a pair differed and was normalized.

Notes:
- Pair detection: files whose stem (minus trailing "_cleaned") matches r"^(.*?)(Yes|No)$" (case-insensitive).
  The "base" is group(1) and the class is Yes/No.
- Files that are not part of a Yes/No pair are processed individually using their own max length.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict

# <<< EDIT THESE PATHS >>>
INPUT_FOLDER = Path("DSPPpatternsU1Cleaned")        # folder with input .txt files
OUTPUT_FOLDER = Path("DSPPpatternsU1CleanedWKEA")   # folder for cleaned files
MAX_LINES = 500

TAG_PATTERN = re.compile(r'^#\w+:$')          # e.g., #UTIL:  #BOND:
INT_PATTERN = re.compile(r'^[+-]?\d+$')       # integer tokens
STRIP_CLEANED_SUFFIX = re.compile(r'(?:_cleaned)+$', re.IGNORECASE)
PAIR_STEM_PATTERN = re.compile(r'^(?P<base>.*?)(?P<cls>Yes|No)$', re.IGNORECASE)


def clean_line(line: str) -> List[str]:
    """
    Clean one line and return the list of positive integer strings kept.
    - Remove tags and their immediate values
    - Keep only positive integers (> 0)
    """
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
        # ignore everything else (floats, words, symbols, etc.)

    return cleaned


def collect_kept_lines(input_path: Path, max_lines: int = 500) -> List[List[str]]:
    """
    Read a file, clean lines, keep only those with >=3 integers, up to max_lines.
    Return a list of integer-string lists (no commas yet).
    """
    kept: List[List[str]] = []
    with input_path.open('r', encoding='utf-8', errors='ignore') as fin:
        for raw in fin:
            ints = clean_line(raw)
            if len(ints) >= 3:
                kept.append(ints)
                if len(kept) >= max_lines:
                    break
    return kept


def write_lines(kept_lines: List[List[str]], output_path: Path, target_len: int) -> int:
    """
    Write kept_lines to output_path, joining with commas and padding with '?'
    up to target_len. Return number of lines written.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as fout:
        for ints in kept_lines:
            if len(ints) < target_len:
                ints = ints + ['?'] * (target_len - len(ints))
            fout.write(','.join(ints) + '\n')
    return len(kept_lines)


def core_stem(stem: str) -> str:
    """
    Remove trailing '_cleaned' (possibly repeated) from a stem for pair detection.
    """
    return STRIP_CLEANED_SUFFIX.sub('', stem)


def detect_pair(stem: str):
    """
    Given a core stem, detect (base, class) where class in {Yes, No} (case-insensitive).
    Returns (base, norm_class) or (None, None) if not matched.
    """
    m = PAIR_STEM_PATTERN.match(stem)
    if not m:
        return None, None
    base = m.group('base')
    cls = m.group('cls').capitalize()  # normalize to 'Yes' or 'No'
    return base, cls


def main():
    if not INPUT_FOLDER.exists() or not INPUT_FOLDER.is_dir():
        raise SystemExit(f"Input folder not found: {INPUT_FOLDER}")

    txt_files = list(INPUT_FOLDER.glob("*.txt"))
    if not txt_files:
        raise SystemExit(f"No .txt files found in {INPUT_FOLDER}")

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    # Group files into pairs by (base -> {Yes: Path, No: Path})
    pairs: Dict[str, Dict[str, Path]] = {}
    singles: List[Path] = []

    for f in txt_files:
        base, cls = detect_pair(core_stem(f.stem))
        if base is None:
            singles.append(f)
        else:
            key = base.upper()  # case-insensitive grouping
            pairs.setdefault(key, {})
            pairs[key][cls] = f

    # Process pairs with normalization
    for key, mapping in pairs.items():
        # Collect kept lines for each present class
        kept_yes = collect_kept_lines(mapping['Yes'], MAX_LINES) if 'Yes' in mapping else []
        kept_no  = collect_kept_lines(mapping['No'],  MAX_LINES) if 'No'  in mapping else []

        max_yes = max((len(x) for x in kept_yes), default=0)
        max_no  = max((len(x) for x in kept_no),  default=0)
        target_len = max(max_yes, max_no)

        # Write outputs with the pair-normalized target_len
        if 'Yes' in mapping:
            out_yes = OUTPUT_FOLDER / f"{mapping['Yes'].stem}_cleaned.txt"
            written_yes = write_lines(kept_yes, out_yes, target_len)
            print(f"Processed {mapping['Yes'].name} -> {out_yes.name} (lines={written_yes}, max_len={target_len})")
            if written_yes < MAX_LINES:
                print(f"⚠️  Warning: {out_yes.name} has only {written_yes} lines (less than {MAX_LINES}).")

        if 'No' in mapping:
            out_no = OUTPUT_FOLDER / f"{mapping['No'].stem}_cleaned.txt"
            written_no = write_lines(kept_no, out_no, target_len)
            print(f"Processed {mapping['No'].name} -> {out_no.name} (lines={written_no}, max_len={target_len})")
            if written_no < MAX_LINES:
                print(f"⚠️  Warning: {out_no.name} has only {written_no} lines (less than {MAX_LINES}).")

        # If both present and differ, print normalization note
        if ('Yes' in mapping) and ('No' in mapping) and (max_yes != max_no):
            base_display = key  # already uppercase
            diff = abs(max_yes - max_no)
            taller = "Yes" if max_yes > max_no else "No"
            shorter = "No" if taller == "Yes" else "Yes"
            print(f"ℹ️  Normalized pair '{base_display}': target_len={target_len} "
                  f"(original {taller}={max(max_yes, max_no)}, {shorter}={min(max_yes, max_no)}; "
                  f"{shorter} padded with {diff} '?').")

    # Process singles (not part of a Yes/No pair): use per-file own max
    for f in singles:
        kept = collect_kept_lines(f, MAX_LINES)
        own_max = max((len(x) for x in kept), default=0)
        out = OUTPUT_FOLDER / f"{f.stem}_cleaned.txt"
        written = write_lines(kept, out, own_max)
        print(f"Processed {f.name} -> {out.name} (lines={written}, max_len={own_max})")
        if written < MAX_LINES:
            print(f"⚠️  Warning: {out.name} has only {written} lines (less than {MAX_LINES}).")


if __name__ == "__main__":
    main()
