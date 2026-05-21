#!/usr/bin/env python3
"""
extract-text.py — Raw paragraph dump from Extra Class DOCX.

Writes every paragraph to text-capture.txt, one per line.
Empty paragraphs become blank lines.
No parsing or restructuring — pure raw dump.
"""

from pathlib import Path
from docx import Document

HERE   = Path(__file__).resolve().parent
DOCX   = HERE / "2024-2028 Extra Class Question Pool and Syllabus Public Release with 4th Errata Feb 4 2026.docx"
OUTPUT = HERE / "text-capture.txt"


def main():
    doc = Document(DOCX)

    lines = []
    for para in doc.paragraphs:
        lines.append(para.text)

    total     = len(lines)
    non_empty = sum(1 for l in lines if l.strip())

    OUTPUT.write_text('\n'.join(lines), encoding='utf-8')

    print(f"Total paragraphs : {total}")
    print(f"Non-empty        : {non_empty}")
    print(f"Written          : {OUTPUT}")


if __name__ == '__main__':
    main()
