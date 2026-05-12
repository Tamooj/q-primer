#!/usr/bin/env python3
"""
indent-pass.py — Apply Java brace-depth indentation to AP CS test source.

Reads:  AP CS Test - enriched.txt
Writes: AP CS Test - indented.txt

Algorithm:
  - Strip leading whitespace from every non-blank line.
  - Track brace depth by counting { and } on each line.
  - Lines that START with } are indented at (depth-1); all others at depth.
  - Depth is updated after placing the line.
  - Blank lines and ~~ separators pass through unchanged.
  - "Line N: code" lines (Q18-19 preamble) keep their prefix; indentation
    is applied to the code portion only.
"""

import re
from pathlib import Path

HERE    = Path(__file__).resolve().parent
SRC     = HERE / "AP CS Test - enriched.txt"
DST     = HERE / "AP CS Test - indented.txt"

LINENO_RE = re.compile(r'^(Line \d+:\s*)(.*)')
INDENT    = "    "   # 4 spaces per depth level


def reindent(stripped: str, depth: int):
    """Return (indented_line, new_depth)."""
    opens  = stripped.count('{')
    closes = stripped.count('}')
    net    = opens - closes

    if stripped.startswith('}'):
        # Closing token leads — step down first, then write
        effective = max(0, depth - 1)
        new_depth = max(0, depth + net)   # net is ≤0 for bare }, =0 for } else {
        return INDENT * effective + stripped, new_depth
    else:
        new_depth = max(0, depth + net)
        return INDENT * depth + stripped, new_depth


def process(lines):
    out   = []
    depth = 0

    for raw in lines:
        line     = raw.rstrip('\n')
        stripped = line.strip()

        # Pass-through: blank lines and separators
        if not stripped or stripped == '~~':
            out.append(line)
            continue

        # "Line N: <code>" format — keep prefix, indent code portion
        lm = LINENO_RE.match(stripped)
        if lm:
            prefix = lm.group(1)
            code   = lm.group(2).strip()
            if code:
                indented_code, depth = reindent(code, depth)
                out.append(prefix + indented_code)
            else:
                out.append(prefix)
            continue

        # All other lines
        indented, depth = reindent(stripped, depth)
        out.append(indented)

    return out


def main():
    with open(SRC, encoding='utf-8') as f:
        lines = f.readlines()

    result = process(lines)

    with open(DST, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
        if not result[-1].endswith('\n'):
            f.write('\n')

    # Sanity check: depth should be 0 at end of file
    # Re-run depth tracking to verify
    depth = 0
    for line in result:
        s = line.strip()
        if s and s != '~~':
            lm = LINENO_RE.match(s)
            code = lm.group(2).strip() if lm else s
            opens  = code.count('{')
            closes = code.count('}')
            if code.startswith('}'):
                depth = max(0, depth - 1)
                depth = max(0, depth + opens)
            else:
                depth = max(0, depth + opens - closes)

    if depth != 0:
        print(f"WARNING: brace depth ended at {depth} (expected 0) — unbalanced braces in source")
    else:
        print("Brace depth OK (ends at 0)")

    print(f"Written: {DST.name}  ({len(result)} lines)")


if __name__ == "__main__":
    main()
