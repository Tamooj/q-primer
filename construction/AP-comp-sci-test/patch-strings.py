#!/usr/bin/env python3
"""
patch-strings.py — Apply targeted string fixes to staging/bank.json.

Fixes three categories of semantic rendering problems:

  1. Q14  — program output display in question body
             single-\n lines would space-join into one run-on line;
             wrap in <code> so each output line displays on its own line.

  2. Q17  — answer choices are program output (what gets printed to console)
             same problem; wrap each answer choice in <code>.

  3. Q39  — "Method N" label runs into its description with a space;
             replace \n between label and description with \n\n.

Run after generate-json.py and format-reference.py.
Safe to re-run; the patches are idempotent.
"""

import json
import re
from pathlib import Path

BANK = Path(__file__).resolve().parent / "staging" / "bank.json"


def patch_q14(q):
    """Wrap the program output block in a <code> block."""
    # The output block is the run of lines like "6 5 4 3 2 1\n5 4 3 2 1\n..."
    # It sits between \n\n and \n\n in the question text.
    old = ('Consider the following output:\n\n'
           '6 5 4 3 2 1\n5 4 3 2 1\n4 3 2 1\n3 2 1\n2 1\n1\n\n'
           'Which of the following code segments produces the above output when executed?')
    new = ('Consider the following output:\n\n'
           '<code>\n6 5 4 3 2 1\n5 4 3 2 1\n4 3 2 1\n3 2 1\n2 1\n1\n</code>\n\n'
           'Which of the following code segments produces the above output when executed?')
    if q['question'] == old:
        q['question'] = new
        return True
    return False


def patch_q17(q):
    """Wrap each answer choice (program output) in a <code> block."""
    changed = False
    for key, val in q['answers'].items():
        if '<code>' not in val and '\n' in val:
            q['answers'][key] = f'<code>\n{val}\n</code>'
            changed = True
    return changed


def patch_q39(q):
    """Add \n\n between each Method label and its description."""
    text = q['question']
    # "Method N\n<description>" -> "Method N\n\n<description>"
    # Match "Method " followed by a digit, then single \n (not double)
    patched = re.sub(r'(Method \d)\n(?!\n)', r'\1\n\n', text)
    # Also ensure the final description line before "Which of the following"
    # gets a paragraph break (it ends with a sentence, then \nWhich...)
    patched = re.sub(r'(find the target word\.)\n(Which of)', r'\1\n\n\2', patched)
    if patched != text:
        q['question'] = patched
        return True
    return False


def main():
    with open(BANK, encoding='utf-8') as f:
        bank = json.load(f)

    questions = {q['id']: q for q in bank['questions']}
    changes = []

    if patch_q14(questions['Q14']):
        changes.append('Q14: wrapped output display in <code>')

    if patch_q17(questions['Q17']):
        changes.append('Q17: wrapped answer choices in <code>')

    if patch_q39(questions['Q39']):
        changes.append('Q39: added paragraph breaks after Method labels')

    if changes:
        with open(BANK, 'w', encoding='utf-8') as f:
            json.dump(bank, f, indent=2, ensure_ascii=False)
        for c in changes:
            print(f'  Patched: {c}')
        print(f'Written: {BANK.name}')
    else:
        print('No changes needed (already patched or strings did not match).')


if __name__ == '__main__':
    main()
