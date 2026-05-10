#!/usr/bin/env python3
"""
build-bank.py  —  Assemble a Q-Primer bank ZIP from a staging directory.

Usage:
    python build-bank.py <staging-dir>

Where <staging-dir> is a subdirectory of construction/ containing:
    bank.json       the question bank
    figures/        PNG files referenced by bank.json (may be empty or absent
                    for text-only banks)

Output:
    banks/<pool_id>.zip   (pool_id is taken from bank.json meta.pool_id)

The script verifies that every figure file referenced in bank.json exists
before creating the archive, and reports any missing files as errors.
"""

import sys
import json
import zipfile
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python build-bank.py <staging-dir>")
        print("  e.g. python build-bank.py ham-general-sample")
        sys.exit(1)

    staging_name = sys.argv[1]
    script_dir   = Path(__file__).resolve().parent
    staging      = script_dir / staging_name

    if not staging.is_dir():
        print(f"Error: staging directory not found: {staging}")
        sys.exit(1)

    bank_json_path = staging / "bank.json"
    if not bank_json_path.exists():
        print(f"Error: bank.json not found in {staging}")
        sys.exit(1)

    # Parse bank.json
    try:
        with open(bank_json_path, "r", encoding="utf-8") as f:
            bank = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in bank.json — {e}")
        sys.exit(1)

    pool_id = bank.get("meta", {}).get("pool_id")
    if not pool_id:
        print("Error: bank.json is missing meta.pool_id")
        sys.exit(1)

    # Collect figure references
    figure_refs = []
    for q in bank.get("questions", []):
        fig = q.get("figure")
        if fig and fig.get("file"):
            figure_refs.append((q["id"], fig["file"]))

    # Verify all referenced figures exist
    figures_dir = staging / "figures"
    missing = []
    for qid, filename in figure_refs:
        if not (figures_dir / filename).exists():
            missing.append(f"  {qid}: figures/{filename}")

    if missing:
        print("Error: the following figure files are referenced in bank.json but not found:")
        for m in missing:
            print(m)
        sys.exit(1)

    # Warn about unreferenced images in figures/
    if figures_dir.exists():
        referenced = {filename for _, filename in figure_refs}
        extra = [f.name for f in figures_dir.iterdir()
                 if f.is_file() and not f.name.startswith(".") and f.name not in referenced]
        if extra:
            print(f"Warning: figures/ contains files not referenced in bank.json:")
            for name in sorted(extra):
                print(f"  {name}")

    # Output path
    out_dir  = script_dir.parent / "banks"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{pool_id}.zip"

    # Build the archive (deduplicate figure filenames — multiple questions may share one figure)
    unique_figures = dict.fromkeys(filename for _, filename in figure_refs)  # preserves order
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(bank_json_path, "bank.json")
        for filename in unique_figures:
            zf.write(figures_dir / filename, f"figures/{filename}")

    # Report
    print(f"Created: {out_path.relative_to(script_dir.parent)}")
    print(f"  bank.json")
    for filename in sorted(unique_figures):
        print(f"  figures/{filename}")
    print(f"  ({len(unique_figures)} figure(s), "
          f"{len(bank.get('questions', []))} question(s))")


if __name__ == "__main__":
    main()
