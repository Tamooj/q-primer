# Preamble Feature — Design Spec
## Q-Primer Schema v1.2

---

## Overview

Some questions require the student to read a block of reference material before
answering — a code listing, class definition, prose description, or mixed
content. These **preambles** are distinct from figures (images) and from the
question text itself. A preamble may be shared across several consecutive
questions.

This feature was designed for the AP Computer Science question pools, where
questions frequently reference Java class definitions and code segments, but
the mechanism is subject-agnostic.

---

## Relationship to Existing Fields

| Field | Type | Scope | Rendered as |
|-------|------|-------|-------------|
| `figure` | image file in ZIP | per-question | inline image |
| `preamble` | text file in ZIP | per-question (may be shared by referencing the same file) | collapsible panel above question |
| `meta.reference_sheet` | inline string in JSON | global (all questions) | modal opened by session-bar button |

These are independent fields. A question may have a figure, a preamble, both,
or neither.

---

## Markup Convention

Preamble files, `meta.reference_sheet`, question text, and answer text all
support the same lightweight markup. Three constructs are recognised:

### Inline code — backticks (preferred)

```
Class Table has a method, `getPrice`, which returns the price.
```

Backtick pairs render as a monospace inline `<code>` span. Use for
identifiers, class names, variable names, and short expressions. This is
the preferred form because it is compact and readable in source — especially
when a sentence references many names.

### Block code — `<code>` tags

```
<code>
public double getPrice() {
    double total = myTable.getPrice();
    for (Chair c : myChairs) total += c.getPrice();
    return total;
}
</code>
```

Content with newlines renders as a scrollable `<pre><code>` block.
Leading and trailing newlines are trimmed automatically.

`<code>expr</code>` (no newlines) also renders as an inline span — this
form still works but backtick is preferred for inline use.

### Tables — `<table>` tag with pipe-delimited rows

```
<table>
|        | Method 1 | Method 2 | Method 3 |
|--------|----------|----------|----------|
| (A)    | 10       | 50       | 1,000    |
| (B)    | 55       | 500      | 2,500    |
| (C)    | 55       | 525      | 25,000   |
| (D)    | 60       | 1,050    | 1,050    |
| (E)    | 60       | 1,050    | 50,000   |
</table>
```

- First non-separator row becomes `<thead>`; remaining rows become `<tbody>`
- Markdown-style separator rows (`|---|---|`) are silently ignored
- Leading/trailing `|` characters are optional
- Table cells support backtick inline code
- Row labels like `(A)`–`(E)` in the first column are styled as muted
  identifiers to distinguish them from data cells

### Rules

- These are the only three constructs. Any other HTML-like tag renders as
  literal text via `textContent` — no `innerHTML` is ever used.
- For long code listings, use a preamble file rather than embedding in a
  question JSON string.

### Mixed preamble example

```
Class `DiningRoomSet` has a constructor which is passed a `Table` object
and an `ArrayList` of `Chair` objects. It stores these in `myTable` and
`myChairs`.

The `getPrice` method returns the sum of the table price and all chair prices:

<code>
public double getPrice() {
    double total = myTable.getPrice();
    for (Chair c : myChairs) total += c.getPrice();
    return total;
}
</code>

Questions 12–13 refer to this implementation.
```

---

## Schema Change — `preamble` Field

Added as an optional field on the question object, parallel to `figure`.
Omit entirely when not needed — do not write `"preamble": null`.

```json
{
  "id": "APCS1-Q06",
  "subelement": "...",
  "group": "...",
  "question": "What is the output of <code>getPrice()</code> when called on a DiningRoomSet with one table priced at 200 and two chairs priced at 50 each?",
  "preamble": {
    "file": "q06-07-dining-room.txt",
    "label": "Table, Chair, and DiningRoomSet class descriptions"
  },
  "answers": { "A": "200", "B": "300", "C": "250", "D": "100", "E": "400" },
  "correct": "B",
  "reference": null,
  "annotation": null
}
```

### `preamble` Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | string | Yes | Filename only — no path. File must exist at `preambles/{file}` inside the ZIP. |
| `label` | string | Yes | Short description shown on the collapsible panel header. |

---

## ZIP Delivery

Banks with preambles must be delivered as ZIP archives. The ZIP structure
extends to include a `preambles/` directory:

```
bank.json
figures/
  G7-1.png
preambles/
  q01-trial-methods.txt
  q06-07-dining-room.txt
  q12-13-insert-sort.txt
```

- Preamble files are plain text (`.txt`). The `<code>` tag convention applies.
- Multiple questions may reference the same preamble file. The file is
  extracted from the ZIP exactly once.
- `build-bank.py` verifies that every `preamble.file` reference exists under
  `preambles/` and includes those files in the archive, mirroring the existing
  figure validation logic.

---

## `meta.reference_sheet` Field (Global Context)

Some exams provide a reference sheet available to the student for the entire
exam — not tied to any individual question. The AP CS A Java Quick Reference
is the canonical example.

Stored in `meta`, not on individual questions. The `<code>` tag convention
applies to its content.

```json
"meta": {
  ...
  "reference_sheet": "class java.lang.String\n  <code>int length()</code>\n  <code>String substring(int from, int to)</code>\n  ..."
}
```

**App behaviour:**
- A **"Reference Sheet"** button appears in the session bar when
  `meta.reference_sheet` is present.
- Clicking the button opens a full-screen modal overlay showing the content
  rendered with `<code>` tag support. Clicking outside the panel or the ✕
  button dismisses it.
- The reference sheet text is injected (tags stripped) into the AI coach
  system prompt for every question.

---

## App Rendering — Preamble

The preamble is rendered as a collapsible `<details>/<summary>` block
positioned **above the question text**, open by default. The student can
collapse it to save screen space.

The AI coach receives the full preamble text (tags stripped) injected into
the per-question user message, regardless of whether the student has the
panel open.

---

## Validation Rules (additions to v1.1)

9. If `preamble` present: both `preamble.file` and `preamble.label` must be
   non-empty strings
10. If any question has a `preamble`, the bank must be delivered as a ZIP and
    `preambles/{file}` must exist in the archive

---

*Schema version: 1.2 — adds `preamble` field, `meta.reference_sheet`, and
`<code>` tag markup convention for question/answer/preamble/reference_sheet text.*
