#!/usr/bin/env python3
"""
build-bank.py  —  Assemble a Q-Primer bank ZIP from a staging directory.

Usage:
    python build-bank.py <staging-dir>

Where <staging-dir> is a subdirectory of construction/ containing:
    bank.json       the question bank
    figures/        image files referenced by bank.json (may be absent)
    preambles/      .txt files referenced by bank.json  (may be absent)

Output:
    banks/<pool_id>.zip   (pool_id is taken from bank.json meta.pool_id)

The script verifies that every figure and preamble file referenced in
bank.json exists before creating the archive, and reports missing files
as errors.
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

    # ── Collect references ────────────────────────────────────────────────
    figure_refs   = []
    preamble_refs = []
    for q in bank.get("questions", []):
        fig = q.get("figure")
        if fig and fig.get("file"):
            figure_refs.append((q["id"], fig["file"]))
        pre = q.get("preamble")
        if pre and pre.get("file"):
            preamble_refs.append((q["id"], pre["file"]))

    # ── Verify figures ────────────────────────────────────────────────────
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

    # Warn about unreferenced files in figures/
    if figures_dir.exists():
        referenced = {filename for _, filename in figure_refs}
        extra = [f.name for f in figures_dir.iterdir()
                 if f.is_file() and not f.name.startswith(".") and f.name not in referenced]
        if extra:
            print("Warning: figures/ contains files not referenced in bank.json:")
            for name in sorted(extra):
                print(f"  {name}")

    # ── Verify preambles ──────────────────────────────────────────────────
    preambles_dir = staging / "preambles"
    missing_pre = []
    for qid, filename in preamble_refs:
        if not (preambles_dir / filename).exists():
            missing_pre.append(f"  {qid}: preambles/{filename}")
    if missing_pre:
        print("Error: the following preamble files are referenced in bank.json but not found:")
        for m in missing_pre:
            print(m)
        sys.exit(1)

    # Warn about unreferenced files in preambles/
    if preambles_dir.exists():
        referenced_pre = {filename for _, filename in preamble_refs}
        extra_pre = [f.name for f in preambles_dir.iterdir()
                     if f.is_file() and not f.name.startswith(".") and f.name not in referenced_pre]
        if extra_pre:
            print("Warning: preambles/ contains files not referenced in bank.json:")
            for name in sorted(extra_pre):
                print(f"  {name}")

    # ── Build archive ─────────────────────────────────────────────────────
    out_dir  = script_dir.parent / "banks"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{pool_id}.zip"

    # Deduplicate — multiple questions may reference the same file
    unique_figures   = dict.fromkeys(filename for _, filename in figure_refs)
    unique_preambles = dict.fromkeys(filename for _, filename in preamble_refs)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(bank_json_path, "bank.json")
        for filename in unique_figures:
            zf.write(figures_dir / filename, f"figures/{filename}")
        for filename in unique_preambles:
            zf.write(preambles_dir / filename, f"preambles/{filename}")

    # ── Report ────────────────────────────────────────────────────────────
    print(f"Created: {out_path.relative_to(script_dir.parent)}")
    print(f"  bank.json")
    for filename in sorted(unique_figures):
        print(f"  figures/{filename}")
    for filename in sorted(unique_preambles):
        print(f"  preambles/{filename}")
    print(f"  ({len(unique_figures)} figure(s), "
          f"{len(unique_preambles)} preamble(s), "
          f"{len(bank.get('questions', []))} question(s))")


if __name__ == "__main__":
    main()
