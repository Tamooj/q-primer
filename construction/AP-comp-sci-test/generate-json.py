#!/usr/bin/env python3
"""
generate-json.py — Build AP CS practice test bank.json from code-tagged.txt.

Reads:  AP CS Test - code-tagged.txt
Writes: staging/bank.json
        staging/preambles/q{N}-{M}.txt   (one per Questions N–M block)

Parsing rules:
  - Blocks are delimited by ~~ lines.
  - A block with no "N. (X)" line is a preamble block.
  - A block with a "N. (X)" line is a question block.
  - In a question block, lines matching ^(A)-(E) start answer choices.
  - Everything before the first (A) line is question text.
  - Answer text is collected until the next label or end of block.
"""

import json
import re
from pathlib import Path

HERE    = Path(__file__).resolve().parent
SRC     = HERE / "AP CS Test - code-tagged.txt"
STAGING = HERE / "staging"

QUESTION_HDR = re.compile(r'^(\d+)\.\s+\(([A-E])\)\s*(.*)')
ANSWER_LBL   = re.compile(r'^\(([A-E])\)\s*(.*)')
PREAMBLE_HDR = re.compile(r'^Questions\s+(\d+)[–\-]+(\d+)\s+refer')

META = {
    'title': 'AP Computer Science Practice Test 1',
    'subtitle': 'Multiple Choice — 40 Questions',
    'pool_id': 'ap-cs-practice-1',
    'version': '1.0',
    'total_questions': 40,
    'passing_score': None,
    'exam_question_count': 40,
    'source_url': None,
    'description': (
        'AP Computer Science A practice test covering object-oriented programming, '
        'arrays, loops, recursion, sorting, searching, and Java fundamentals.'
    ),
    'tags': ['AP', 'computer science', 'Java', 'OOP'],
    'reference_sheet': None,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def split_blocks(lines):
    """Yield each ~~ -separated block as a list of strings."""
    current = []
    for line in lines:
        if line.strip() == '~~':
            if any(l.strip() for l in current):
                yield list(current)
            current = []
        else:
            current.append(line)
    if any(l.strip() for l in current):
        yield list(current)


def trim_blanks(lines):
    """Return new list with leading/trailing blank lines removed."""
    ls = list(lines)
    while ls and not ls[0].strip():
        ls.pop(0)
    while ls and not ls[-1].strip():
        ls.pop()
    return ls


def to_text(lines):
    """
    Join lines into a string with HTML-aware newline handling.

    The app renderer treats \n as a space and \n\n as a paragraph break.
    This function ensures <code> blocks are always paragraph-separated from
    surrounding prose so they render as block elements rather than inline runs.
    """
    joined = '\n'.join(trim_blanks(list(lines)))
    # Ensure <code> opens on its own paragraph
    joined = re.sub(r'([^\n])\n(<code>)', r'\1\n\n\2', joined)
    # Ensure </code> is followed by a paragraph break before any prose
    joined = re.sub(r'(</code>)\n([^\n])', r'\1\n\n\2', joined)
    # Collapse any triple+ newlines introduced above
    joined = re.sub(r'\n{3,}', '\n\n', joined)
    return joined.strip()


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def is_question_block(lines):
    return any(QUESTION_HDR.match(l.strip()) for l in lines)


def parse_preamble(lines):
    """
    Parse a preamble block.
    Returns (filename, label, n_start, n_end, content_str) or None.
    """
    content = trim_blanks(lines)
    if not content:
        return None
    first = content[0].strip()
    m = PREAMBLE_HDR.match(first)
    if not m:
        return None
    n_start = int(m.group(1))
    n_end   = int(m.group(2))
    filename = f'q{n_start:02d}-{n_end:02d}.txt'
    # Reconstruct label with a clean en-dash (source encoding may have corrupted it)
    label = f"Questions {n_start}–{n_end} refer{first[m.end():]}"
    body     = to_text(content[1:])
    return filename, label, n_start, n_end, body


def parse_question(lines):
    """
    Parse a question block.
    Returns dict: {q_num, correct, question, answers} or None.
    """
    # Locate the question header
    hdr_idx = q_num = correct = first_text = None
    for i, line in enumerate(lines):
        m = QUESTION_HDR.match(line.strip())
        if m:
            hdr_idx   = i
            q_num     = int(m.group(1))
            correct   = m.group(2)
            first_text = m.group(3).strip()
            break

    if hdr_idx is None:
        return None

    # Walk lines after the header, splitting question text from answer choices
    q_parts  = [first_text] if first_text else []
    answers  = {}
    cur_label = None
    cur_lines = []
    in_answers = False

    for line in lines[hdr_idx + 1:]:
        s = line.strip()
        m = ANSWER_LBL.match(s)

        if m:
            # Save previous answer choice
            in_answers = True
            if cur_label is not None:
                answers[cur_label] = to_text(cur_lines)
            cur_label = m.group(1)
            rest = m.group(2)
            cur_lines = [rest] if rest else []
        elif in_answers:
            # Continuation of current answer choice (may include <code> blocks)
            cur_lines.append(line)
        else:
            # Still in question text
            q_parts.append(line)

    if cur_label is not None:
        answers[cur_label] = to_text(cur_lines)

    return {
        'q_num':   q_num,
        'correct': correct,
        'question': to_text(q_parts),
        'answers':  answers,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    with open(SRC, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f.readlines()]

    preamble_dir = STAGING / 'preambles'
    preamble_dir.mkdir(parents=True, exist_ok=True)

    preamble_map  = {}   # int q_num -> {'file': ..., 'label': ...}
    questions_raw = []

    for block in split_blocks(lines):
        trimmed = trim_blanks(block)
        if not trimmed:
            continue

        if is_question_block(trimmed):
            q = parse_question(trimmed)
            if q:
                questions_raw.append(q)
        else:
            result = parse_preamble(trimmed)
            if result:
                filename, label, n_start, n_end, body = result
                (preamble_dir / filename).write_text(body, encoding='utf-8')
                preamble_info = {'file': filename, 'label': label}
                for n in range(n_start, n_end + 1):
                    preamble_map[n] = preamble_info
                print(f"  Preamble Q{n_start}-{n_end} -> {filename}  ({len(body)} chars)")
            else:
                first = trimmed[0].strip()
                print(f"  WARNING: unrecognised non-question block: {first[:70]!r}")

    questions_raw.sort(key=lambda q: q['q_num'])

    # Build question objects
    questions = []
    for q in questions_raw:
        n = q['q_num']
        qobj = {
            'id':        f'Q{n:02d}',
            'question':  q['question'],
            'answers':   q['answers'],
            'correct':   q['correct'],
            'reference': '',
            'annotation': None,
        }
        if n in preamble_map:
            qobj['preamble'] = preamble_map[n]
        questions.append(qobj)

    META['total_questions'] = len(questions)
    bank = {'meta': META, 'questions': questions}

    out_path = STAGING / 'bank.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    print(f"\nWritten: {out_path}  ({len(questions)} questions)")
    print(f"Preamble coverage: {sorted(preamble_map.keys())}")

    # Validation
    errors = 0
    for q in questions:
        qid = q['id']
        if q['correct'] not in q['answers']:
            print(f"ERROR {qid}: correct={q['correct']!r} not in {list(q['answers'].keys())}")
            errors += 1
        for k, v in q['answers'].items():
            if not v.strip():
                print(f"WARNING {qid}: answer {k} is empty")
                errors += 1

    if errors == 0:
        print("Validation: OK")
    else:
        print(f"Validation: {errors} error(s)")


if __name__ == '__main__':
    main()
