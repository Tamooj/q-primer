#!/usr/bin/env python3
"""
format-reference.py — Format Java-reference.txt for meta.reference_sheet.

Reads:  Java-reference.txt
Writes: staging/reference_sheet.txt  (for review)
Patches: staging/bank.json  meta.reference_sheet

Output format:
  class `java.lang.String`

  <table>
  | Method | Description |
  |--------|-------------|
  | `int length()` | |
  | `String substring(int from, int to)` | returns the substring... |
  </table>
"""

import json
import re
from pathlib import Path

HERE  = Path(__file__).resolve().parent
SRC   = HERE / "Java-reference.txt"
BANK  = HERE / "staging" / "bank.json"
DRAFT = HERE / "staging" / "reference_sheet.txt"


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_reference(lines):
    """
    Return list of (header_str, methods_list).
    methods_list is list of (sig_str, desc_str).
    """
    sections = []
    cur_header = None
    cur_methods = []
    cur_sig = None
    cur_desc = []

    def flush_method():
        nonlocal cur_sig, cur_desc
        if cur_sig is not None:
            # Join: "; " before parts that start new sentences ("returns ..."),
            # plain " " for mid-sentence wraps
            joined = ''
            for i, part in enumerate(cur_desc):
                if i == 0:
                    joined = part
                elif part.lower().startswith('returns'):
                    joined = joined.rstrip(';').rstrip() + '; ' + part
                else:
                    joined += ' ' + part
            cur_methods.append((cur_sig, joined))
        cur_sig = None
        cur_desc = []

    def flush_section():
        nonlocal cur_header, cur_methods
        if cur_header is not None:
            flush_method()
            sections.append((cur_header, list(cur_methods)))
        cur_header = None
        cur_methods = []

    for raw in lines:
        s = raw.rstrip().strip()

        if not s:
            continue

        # Section header
        if s.startswith('class ') or s.startswith('interface '):
            flush_section()
            cur_header = s
            continue

        # Bullet point — new method/field entry
        if s.startswith('•') or s.startswith('*'):
            flush_method()
            rest = s.lstrip('•* ').strip()
            if '//' in rest:
                idx = rest.index('//')
                cur_sig = rest[:idx].strip()
                cur_desc = [rest[idx + 2:].strip()]
            else:
                cur_sig = rest.strip()
                cur_desc = []
            continue

        # Continuation comment
        if s.startswith('//') and cur_sig is not None:
            cur_desc.append(s[2:].strip())
            continue

    flush_section()
    return sections


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def format_reference(sections):
    parts = []

    for header, methods in sections:
        # Header: "class java.lang.String" -> "class `java.lang.String`"
        m = re.match(r'^(class|interface)\s+(.*)', header)
        if m:
            kw, name = m.group(1), m.group(2)
            parts.append(f"{kw} `{name}`")
        else:
            parts.append(f"`{header}`")

        if not methods:
            parts.append('')
            continue

        parts.append('')
        parts.append('<table>')
        parts.append('| Method | Description |')
        parts.append('|--------|-------------|')
        for sig, desc in methods:
            parts.append(f'| `{sig}` | {desc} |')
        parts.append('</table>')
        parts.append('')

    return '\n'.join(parts).strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    with open(SRC, encoding='utf-8') as f:
        lines = f.readlines()

    sections = parse_reference(lines)
    text = format_reference(sections)

    # Write draft for review
    DRAFT.parent.mkdir(parents=True, exist_ok=True)
    DRAFT.write_text(text, encoding='utf-8')
    print(f"Draft written: {DRAFT.name}")
    print()
    print(text)
    print()

    method_count = sum(len(m) for _, m in sections)
    print(f"--- {len(sections)} sections, {method_count} entries ---")

    # Patch bank.json
    with open(BANK, encoding='utf-8') as f:
        bank = json.load(f)

    bank['meta']['reference_sheet'] = text

    with open(BANK, 'w', encoding='utf-8') as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    print(f"Patched: bank.json  (reference_sheet = {len(text)} chars)")


if __name__ == '__main__':
    main()
