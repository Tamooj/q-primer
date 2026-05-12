#!/usr/bin/env python3
"""
code-tag-pass.py — Wrap Java code blocks with <code>...</code> tags.

Reads:  AP CS Test - indented.txt
Writes: AP CS Test - code-tagged.txt

Algorithm:
  Pass 1 — classify each line: CODE | PROSE | BLANK | SEP
  Pass 2 — promote BLANK → CODE_BLANK when sandwiched between CODE lines
  Pass 3 — emit, inserting <code>/<\/code> around contiguous CODE/CODE_BLANK runs

Code detection rules (first match wins):
  - Has leading whitespace                   → CODE
  - Matches "Line N:"  (Q18-19 preamble)     → CODE
  - Starts with // /* */ * (comment)         → CODE
  - Contains { or }                          → CODE
  - Ends with ;                              → CODE
  - First word (or word after Roman "I. ")
    is a Java keyword                        → CODE
  - Contains \breturn\b                      → CODE
  - prev line was CODE and line ends with ,  → CODE (multi-line expr)
  - Contains != == && ||                     → CODE
  Lines starting with (A)-(E) are PROSE regardless.
  Lines matching "N. (X)" question headers are PROSE.
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC  = HERE / "AP CS Test - indented.txt"
DST  = HERE / "AP CS Test - code-tagged.txt"

JAVA_KEYWORDS = {
    'public', 'private', 'protected', 'static', 'void',
    'int', 'double', 'boolean', 'String', 'char', 'float', 'long', 'short', 'byte',
    'for', 'while', 'if', 'else', 'return', 'new', 'class', 'interface',
    'extends', 'implements', 'import', 'abstract', 'super', 'final',
    'null', 'true', 'false',
    'List', 'ArrayList', 'Integer', 'Math', 'System',
    'throws', 'try', 'catch', 'switch', 'case', 'break', 'continue', 'do',
}

QUESTION_RE = re.compile(r'^\d+\. \([A-E]\)')
ANSWER_RE   = re.compile(r'^\([A-E]\)')
LINENO_RE   = re.compile(r'^Line \d+:')
ROMAN_RE    = re.compile(r'^[IVX]+\.\s+(\w+)')


def classify(line, prev_was_code):
    s = line.strip()

    if not s:
        return 'BLANK'
    if s == '~~':
        return 'SEP'

    # Question/answer labels always prose
    if QUESTION_RE.match(s):
        return 'PROSE'
    if ANSWER_RE.match(s):
        return 'PROSE'

    # Indented → code (indent-pass already ran)
    if line != line.lstrip():
        return 'CODE'

    # Line N: format (Q18-19 preamble)
    if LINENO_RE.match(s):
        return 'CODE'

    # Comment lines
    if (s.startswith('//') or s.startswith('/*') or
            s.startswith('*/') or s.startswith('* ') or s == '*'):
        return 'CODE'

    # Braces
    if '{' in s or '}' in s:
        return 'CODE'

    # Ends with semicolon (strip inline // comment first)
    code_part = re.sub(r'\s*//.*$', '', s).rstrip()
    if code_part.endswith(';'):
        return 'CODE'

    # First token is Java keyword; handle "I. return ..." Roman-numeral prefix
    first = s.split()[0]
    m = ROMAN_RE.match(s)
    if m:
        first = m.group(1)
    if first in JAVA_KEYWORDS:
        return 'CODE'

    # return keyword anywhere on the line
    if re.search(r'\breturn\b', s):
        return 'CODE'

    # Continuation: prev line was CODE and this line ends with comma
    if prev_was_code and s.endswith(','):
        return 'CODE'

    # Increment/decrement operators
    if '++' in s or '--' in s:
        return 'CODE'

    # Unambiguous binary operators (exclude == to avoid prose false-positives)
    if re.search(r'!=|&&|\|\|', s):
        return 'CODE'

    return 'PROSE'


def process(lines):
    # --- Pass 1: classify ---
    classes = []
    prev_code = False
    for line in lines:
        c = classify(line.rstrip('\n'), prev_code)
        classes.append(c)
        if c == 'CODE':
            prev_code = True
        elif c != 'BLANK':
            prev_code = False

    # --- Pass 2: promote blanks sandwiched between CODE lines ---
    for i, c in enumerate(classes):
        if c != 'BLANK':
            continue
        # Next non-blank class
        j = i + 1
        while j < len(classes) and classes[j] in ('BLANK', 'CODE_BLANK'):
            j += 1
        next_cls = classes[j] if j < len(classes) else 'EOF'
        # Prev non-blank class
        k = i - 1
        while k >= 0 and classes[k] in ('BLANK', 'CODE_BLANK'):
            k -= 1
        prev_cls = classes[k] if k >= 0 else 'BOF'
        if prev_cls == 'CODE' and next_cls == 'CODE':
            classes[i] = 'CODE_BLANK'

    # --- Pass 3: emit with <code>/<\/code> ---
    out = []
    in_code = False

    for line, cls in zip(lines, classes):
        raw = line.rstrip('\n')
        if cls in ('CODE', 'CODE_BLANK'):
            if not in_code:
                out.append('<code>')
                in_code = True
            out.append(raw)
        else:
            if in_code:
                out.append('</code>')
                in_code = False
            out.append(raw)

    if in_code:
        out.append('</code>')

    return out, classes


def main():
    with open(SRC, encoding='utf-8') as f:
        lines = f.readlines()

    result, classes = process(lines)

    with open(DST, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
        f.write('\n')

    # Stats
    code_count = sum(1 for c in classes if c == 'CODE')
    prose_count = sum(1 for c in classes if c == 'PROSE')
    blank_code = sum(1 for c in classes if c == 'CODE_BLANK')
    print(f"Lines: {len(lines)}  CODE={code_count}  PROSE={prose_count}  "
          f"CODE_BLANK={blank_code}")
    print(f"Written: {DST.name}  ({len(result)} lines)")


if __name__ == '__main__':
    main()
