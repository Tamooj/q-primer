#!/usr/bin/env python3
"""
generate-json.py — Build Extra Class (Element 4) bank.json from text-capture.txt.

Reads:  text-capture.txt
Writes: staging/bank.json

Parsing rules:
  - Split on ~~ lines; each ~~ block is one question (or noise to skip)
  - A block with a line matching ^E\dX\d+ (X) is a question block
  - A block with a line matching ^E\dX\d+ Question Deleted is skipped
  - Everything before the question ID line in a block is ignored (errata/headers)
  - Answer choices start with ^[A-D]\. (e.g. "A. Some text")
  - Figure references auto-detected from question + answer text;
    "Figure E5-1" -> figures/Figure-e5-1.png
"""

import json
import re
import shutil
from pathlib import Path

HERE    = Path(__file__).resolve().parent
SRC     = HERE / "text-capture.txt"
STAGING = HERE / "staging"

QUESTION_HDR = re.compile(r'^(E\d[A-Z]\d+)\s+\(([A-E])\)')   # E1A01 (D) [...]
DELETED_HDR  = re.compile(r'^(E\d[A-Z]\d+)\s+Question\s+Deleted', re.IGNORECASE)
ANSWER_LBL   = re.compile(r'^([A-D])\.\s*(.*)')
FIGURE_REF   = re.compile(r'\bFigure\s+(E\d-\d)\b', re.IGNORECASE)

# Alt text for each figure (accessibility + AI context)
FIGURE_ALTS = {
    'E5-1': 'Complex impedance coordinate plane with eight labeled points (1 through 8) plotted at various resistive and reactive positions, used for series circuit impedance identification.',
    'E6-1': 'Schematic symbols for field-effect transistors, including N-channel dual-gate MOSFET, P-channel junction FET, and other FET variants with labeled terminals.',
    'E6-2': 'Schematic symbols for diode types, including Schottky diode, Zener diode, and other diode variants with standard anode/cathode orientation.',
    'E6-3': 'Schematic symbols for digital logic gates, including NAND, NOR, and NOT (inverter) gates with standard IEEE/ANSI symbol shapes.',
    'E7-1': 'Transistor amplifier circuit schematic showing an NPN BJT with voltage-divider bias resistors R1 and R2, emitter resistor R3, and coupling/bypass capacitors C1, C2, and C3.',
    'E7-2': 'Electronic circuit schematic showing NPN transistor Q1 and LED/diode D1 with supply voltages +25V and +12V, capacitors C1, C2, C3, and resistors R1 and R2.',
    'E7-3': 'Operational amplifier circuit schematic in inverting configuration with input resistor R1, feedback resistor RF, and labeled input/output terminals.',
    'E9-1': 'Polar antenna radiation pattern diagram showing azimuth response with labeled front-to-back ratio, 3 dB beamwidth markers, and directional gain contours.',
    'E9-2': 'Antenna radiation pattern diagram showing both azimuth and elevation response, with labeled elevation angle of peak response and front-to-back ratio.',
    'E9-3': 'Smith chart showing normalized impedance with resistance circles, reactance arcs, the outer reactance axis circle, and the central resistance (real) axis.',
}

META = {
    'title':               'FCC Amateur Extra Class (Element 4) Question Pool',
    'subtitle':            'Multiple Choice — 2024-2028 Pool (4th Errata)',
    'pool_id':             'ham-extra-full',
    'version':             '2024-2028-errata4',
    'total_questions':     None,
    'passing_score':       None,
    'exam_question_count': 50,
    'source_url':          None,
    'description': (
        'FCC Amateur Extra Class (Element 4) question pool, effective July 1, 2024, '
        'with 4th errata issued February 4, 2026. Covers commission rules, operating '
        'procedures, radio wave propagation, amateur practices, electrical principles, '
        'circuit components, practical circuits, signals and emissions, antennas and '
        'transmission lines, and safety.'
    ),
    'tags':            ['FCC', 'amateur radio', 'Extra Class', 'Element 4', 'ham radio'],
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
    ls = list(lines)
    while ls and not ls[0].strip():
        ls.pop(0)
    while ls and not ls[-1].strip():
        ls.pop()
    return ls


def to_text(lines):
    """
    Join lines into a string with HTML-aware newline handling.
    \n -> space, \n\n -> paragraph break in the renderer.
    Ensures <code> blocks are paragraph-separated.
    """
    joined = '\n'.join(trim_blanks(list(lines)))
    joined = re.sub(r'([^\n])\n(<code>)',   r'\1\n\n\2', joined)
    joined = re.sub(r'(</code>)\n([^\n])',  r'\1\n\n\2', joined)
    joined = re.sub(r'\n{3,}', '\n\n', joined)
    return joined.strip()


def figure_filename(ref):
    """'E5-1' -> 'Figure-e5-1.png'"""
    return f"Figure-{ref.lower()}.png"


def figure_obj(ref):
    """'E5-1' -> {'file': 'Figure-e5-1.png', 'alt': '...'}"""
    return {
        'file': figure_filename(ref),
        'alt':  FIGURE_ALTS.get(ref, f'Diagram {ref} referenced in question.'),
    }


def detect_figures(text):
    """Return sorted list of unique figure refs (e.g. 'E5-1') found in text."""
    return sorted({m for m in FIGURE_REF.findall(text)})


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_block(block):
    """
    Parse a ~~ block.
    Returns dict or None.
      - None if no question ID found (noise/header block) or deleted
    """
    lines = trim_blanks(block)

    # Find the question ID line
    hdr_idx = q_id = correct = None
    for i, line in enumerate(lines):
        m = QUESTION_HDR.match(line.strip())
        if m:
            hdr_idx = i
            q_id    = m.group(1)
            correct = m.group(2)
            break
        # Check for deleted marker before committing
        if DELETED_HDR.match(line.strip()):
            return None   # skip deleted

    if hdr_idx is None:
        return None  # no question header found — header/noise block

    # Parse question text and answer choices
    q_parts   = []
    answers   = {}
    cur_label = None
    cur_lines = []
    in_answers = False

    for line in lines[hdr_idx + 1:]:
        s = line.strip()
        m = ANSWER_LBL.match(s)
        if m:
            in_answers = True
            if cur_label is not None:
                answers[cur_label] = to_text(cur_lines)
            cur_label = m.group(1)
            rest = m.group(2)
            cur_lines = [rest] if rest else []
        elif in_answers:
            cur_lines.append(line)
        else:
            q_parts.append(line)

    if cur_label is not None:
        answers[cur_label] = to_text(cur_lines)

    return {
        'id':      q_id,
        'correct': correct,
        'question': to_text(q_parts),
        'answers':  answers,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_pool_start(lines):
    """
    Return the index of the first line of the actual question pool, skipping
    the errata and syllabus sections at the top.

    Strategy: find the line "FCC Element 4 Question Pool" that is immediately
    followed (within a few lines) by "Effective" — this is the pool header,
    not the syllabus header ("FCC Element 4 Question Pool Syllabus").
    """
    for i, line in enumerate(lines):
        if line.strip() == 'FCC Element 4 Question Pool':
            # Check that "Effective" appears within the next 3 lines
            for j in range(i + 1, min(i + 4, len(lines))):
                if lines[j].strip().startswith('Effective'):
                    return i
    return 0   # fallback: process from the beginning


def main():
    with open(SRC, encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f.readlines()]

    pool_start = find_pool_start(lines)
    print(f"Pool starts at line {pool_start + 1}: {lines[pool_start].strip()!r}")
    lines = lines[pool_start:]

    STAGING.mkdir(parents=True, exist_ok=True)

    questions  = []
    skipped    = []
    noise      = 0

    for block in split_blocks(lines):
        result = parse_block(block)
        if result is None:
            # Check whether it was a deleted question or just noise
            trimmed = trim_blanks(block)
            is_deleted = any(DELETED_HDR.match(l.strip()) for l in trimmed)
            if is_deleted:
                for l in trimmed:
                    m = DELETED_HDR.match(l.strip())
                    if m:
                        skipped.append(m.group(1))
                        break
            else:
                noise += 1
            continue

        q_id    = result['id']
        correct = result['correct']
        q_text  = result['question']
        answers = result['answers']

        # Build combined text for figure detection
        all_text = q_text + ' ' + ' '.join(answers.values())
        figs = detect_figures(all_text)

        qobj = {
            'id':         q_id,
            'question':   q_text,
            'answers':    answers,
            'correct':    correct,
            'reference':  '',
            'annotation': None,
        }
        if figs:
            # Most questions reference only one figure; if multiple,
            # use the first (questions typically name only one figure)
            qobj['figure'] = figure_obj(figs[0])
            if len(figs) > 1:
                print(f"  NOTE {q_id}: multiple figures detected: {figs} -> using {figs[0]}")

        questions.append(qobj)

    # Sort by question ID (E1A01, E1A02, ... E9H12, E0A01)
    questions.sort(key=lambda q: q['id'])

    # Copy referenced figures into staging/figures/ so build-bank.py can find them
    figures_src = HERE / 'figures'
    figures_dst = STAGING / 'figures'
    figures_dst.mkdir(parents=True, exist_ok=True)
    referenced_figs = {q['figure']['file'] for q in questions if q.get('figure')}
    for fname in sorted(referenced_figs):
        src = figures_src / fname
        dst = figures_dst / fname
        if src.exists():
            shutil.copy2(src, dst)
        else:
            print(f"  WARNING: source figure not found: {src}")

    META['total_questions'] = len(questions)
    bank = {'meta': META, 'questions': questions}

    out_path = STAGING / 'bank.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)

    print(f"\nWritten: {out_path}  ({len(questions)} questions)")
    print(f"Skipped (deleted): {len(skipped)} -> {skipped}")
    print(f"Noise blocks skipped: {noise}")

    # Figure coverage report
    fig_qs = [(q['id'], q['figure']['file']) for q in questions if 'figure' in q]
    if fig_qs:
        from collections import Counter
        counts = Counter(f for _, f in fig_qs)
        print(f"\nFigure references ({len(fig_qs)} questions across {len(counts)} figures):")
        for fname, count in sorted(counts.items()):
            print(f"  {fname}: {count} question(s)")

    # Validation
    errors = 0
    for q in questions:
        qid = q['id']
        if q['correct'] not in q['answers']:
            print(f"ERROR {qid}: correct={q['correct']!r} not in {list(q['answers'].keys())}")
            errors += 1
        if len(q['answers']) != 4:
            print(f"WARNING {qid}: {len(q['answers'])} answer choices (expected 4)")
            errors += 1
        for k, v in q['answers'].items():
            if not v.strip():
                print(f"WARNING {qid}: answer {k} is empty")
                errors += 1

    if errors == 0:
        print("\nValidation: OK")
    else:
        print(f"\nValidation: {errors} error(s)")


if __name__ == '__main__':
    main()
