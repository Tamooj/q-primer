# Question Bank Schema Specification
## Q-Primer — v1.2

---

## Overview

A question bank is a single JSON file that fully describes a multiple-choice test pool. The app treats the file as a pure data dependency — it contains no subject-specific logic. The app never generates, infers, or modifies question content.

Question banks are portable, versionable, and human-readable. They may be loaded from local file upload or from a remote URL.

---

## Delivery Format

Question banks come in two forms:

**Plain JSON (`.json`)** — text-only banks with no figures or preambles. A single file containing the full schema.

**ZIP archive (`.zip`)** — banks whose questions reference figures (diagrams, schematics, charts) or preamble files. The ZIP must contain:
```
bank.json          — the question bank (full schema, required)
figures/           — directory of image files (PNG, JPG, or other browser-renderable formats)
  G7-1.png
  G3-1.jpg
  ...
preambles/         — directory of plain-text preamble files (present only if any questions use preambles)
  q01-trial-methods.txt
  q06-07-dining-room.txt
  ...
```
`bank.json` references figure files by filename only (not path). The app looks for them under `figures/` inside the ZIP. Preamble files are looked up under `preambles/`. Every filename referenced in `figure.file` or `preamble.file` must exist in the corresponding directory; the build script (`construction/build-bank.py`) enforces this.

The app deduplicates figures and preambles automatically: multiple questions may reference the same file; each file is extracted from the ZIP exactly once.

---

## File Naming Convention

```
{subject-slug}-{pool-id}-{version}.json    (plain JSON)
{pool-id}.zip                              (ZIP with figures and/or preambles)
```

Examples:
- `ham-general-2023-2027-v1.2.json`
- `fcc-element3-2023-2027.zip`
- `us-citizenship-2024-v1.0.json`
- `ap-biology-2025-v1.0.json`

---

## Top-Level Schema

```json
{
  "meta": { ... },
  "structure": { ... },
  "questions": [ ... ]
}
```

---

## `meta` Object

Descriptive information about the bank. Displayed in the app UI and injected into the AI coach system prompt.

```json
"meta": {
  "title": "Ham Radio General Class",
  "subtitle": "FCC Element 3 Question Pool",
  "pool_id": "fcc-element3-2023-2027",
  "version": "1.2",
  "effective_from": "2023-07-01",
  "effective_to": "2027-06-30",
  "total_questions": 429,
  "passing_score": 26,
  "exam_question_count": 35,
  "source_url": "https://www.arrl.org/general-class-question-pool",
  "description": "Official FCC question pool for the Amateur Radio General Class license examination.",
  "tags": ["amateur radio", "FCC", "RF", "electronics"],
  "reference_sheet": null
}
```

### Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | Yes | Display name |
| `subtitle` | string | No | Secondary display line |
| `pool_id` | string | Yes | Unique slug, kebab-case |
| `version` | string | Yes | Semantic version |
| `effective_from` | string | No | ISO 8601 date |
| `effective_to` | string | No | ISO 8601 date |
| `total_questions` | integer | No | Informational |
| `passing_score` | integer | No | Correct answers needed to pass |
| `exam_question_count` | integer | No | Questions drawn on actual exam |
| `source_url` | string | No | Authoritative source |
| `description` | string | No | Injected into AI coach context |
| `tags` | string[] | No | For future filtering/search |
| `reference_sheet` | string\|null | No | Global reference text available for the full exam session. See [`meta.reference_sheet`](#metareference_sheet-field) below. |
| `coach_model` | string | No | Route key controlling which AI model the coach uses. See [Model Routing](#model-routing) below. Omit for default (Haiku). |

---

## Model Routing

The `meta.coach_model` field is an optional route key that controls which AI model the app uses for coaching on this bank. Bank authors set a semantic label; the app maps it to a model.

| Route key | Model | Notes |
|-----------|-------|-------|
| *(absent or unknown)* | `claude-haiku-4-5` | Default — fast, low cost |
| `trivia` | `claude-haiku-4-5` | |
| `history` | `claude-haiku-4-5` | |
| `civics` | `claude-haiku-4-5` | |
| `ap_biology` | `claude-sonnet-4-6` | |
| `ap_chemistry` | `claude-sonnet-4-6` | |
| `ap_physics` | `claude-sonnet-4-6` | |
| `ap_cs_principles` | `claude-sonnet-4-6` | |
| `ap_cs_applied` | `claude-sonnet-4-6` | Future: agent SDK path |
| `ap_calculus` | `claude-sonnet-4-6` | Extended math reasoning |
| `amateur_radio` | `claude-sonnet-4-6` | RF/electronics/regulations |

The routing table lives in `CoachAPI` in `index.html`. Add new keys there when new subjects or models are introduced.

---

## `structure` Object

Defines the hierarchy of the question pool. Optional but enables topic-based filtering ("quiz me on G3 only"). Structure is subject-agnostic — any two-level hierarchy works.

```json
"structure": {
  "levels": ["subelement", "group"],
  "subelements": [
    {
      "id": "G1",
      "title": "Commission's Rules",
      "exam_questions": 5,
      "groups": [
        { "id": "G1A", "title": "General class control operator frequency privileges" },
        { "id": "G1B", "title": "Antenna structure limitations; beacon operation" }
      ]
    },
    {
      "id": "G3",
      "title": "Radio Wave Propagation",
      "exam_questions": 3,
      "groups": [
        { "id": "G3A", "title": "Sunspots and solar radiation" },
        { "id": "G3B", "title": "Maximum Usable Frequency; Lowest Usable Frequency" },
        { "id": "G3C", "title": "Ionospheric regions; critical angle and frequency" }
      ]
    }
  ]
}
```

If `structure` is absent, the app treats the bank as a flat pool with no filtering hierarchy.

---

## `questions` Array

Each element is a question object.

```json
{
  "id": "G1A01",
  "subelement": "G1",
  "group": "G1A",
  "question": "On which HF and/or MF amateur bands are there portions where General class licensees cannot transmit?",
  "answers": {
    "A": "60 meters, 30 meters, 17 meters, and 12 meters",
    "B": "160 meters, 60 meters, 15 meters, and 12 meters",
    "C": "80 meters, 40 meters, 20 meters, and 15 meters",
    "D": "80 meters, 20 meters, 15 meters, and 10 meters"
  },
  "correct": "C",
  "reference": "97.301(d)",
  "figure": null,
  "annotation": null
}
```

### Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | Yes | Unique within bank. Stable identifier. |
| `subelement` | string | No | Must match `structure.subelements[].id` if structure present |
| `group` | string | No | Must match `structure.subelements[].groups[].id` if structure present |
| `question` | string | Yes | Verbatim question text. Never modified by app. Supports markup convention. |
| `answers` | object | Yes | 2–6 keys forming a contiguous sequence from `A` (e.g. `A,B` or `A,B,C,D` or `A`–`F`). All values must be non-empty strings. Supports markup convention. |
| `correct` | string | Yes | Must be one of the keys present in `answers`. |
| `reference` | string | No | Rule citation, chapter reference, etc. Displayed in UI. |
| `figure` | object\|null | No | See [Figure schema](#figure-object) below. Required for questions that reference a diagram. |
| `preamble` | object | No | See [Preamble schema](#preamble-object) below. Omit entirely when not needed — do not write `"preamble": null`. |
| `annotation` | object\|null | No | See [Annotation schema](#annotation-object) below. |

### Answer Key Rules

- `correct` is the **sole authoritative source** for the correct answer
- The app must never derive or infer the correct answer from any other field
- Answer text must be stored verbatim — no reformatting, no punctuation normalization
- Keys must be a **contiguous sequence starting from `A`**: valid sets are `{A,B}`, `{A,B,C}`, `{A,B,C,D}`, `{A,B,C,D,E}`, `{A,B,C,D,E,F}`. Gaps are not allowed (e.g. `{A,C}` is invalid).
- Traditional 4-choice (`A`–`D`) is the default; use fewer or more only when the source material genuinely warrants it

---

## Markup Convention

The following markup constructs are supported in question text, answer text, preamble files, and `meta.reference_sheet`. All rendering is DOM-safe — `textContent` only, never `innerHTML`. Any unrecognized HTML-like tag renders as literal text.

### Inline code — backticks (preferred)

```
Class `Table` has a method, `getPrice`, which returns the price.
```

Backtick pairs render as a monospace inline `<code>` span. Use for identifiers, class names, variable names, and short expressions. Preferred for inline use because it is compact and readable in source — especially when a sentence references many names.

### Block code — `<code>` tag

Content with newlines renders as a scrollable `<pre><code>` block. Leading and trailing newlines are trimmed automatically:

```
<code>
public double getPrice() {
    double total = myTable.getPrice();
    for (Chair c : myChairs) total += c.getPrice();
    return total;
}
</code>
```

`<code>expr</code>` (no newlines) also renders as an inline span — this form still works but backtick is preferred for inline use.

### Tables — `<table>` tag

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
- Row labels like `(A)`–`(E)` in the first column are styled as muted identifiers

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

For long code listings, use a preamble file rather than embedding in a question JSON string.

---

## `figure` Object

Present when a question asks the student to interpret a diagram, schematic, chart, or other image. The bank must be delivered as a ZIP archive when any questions include figures.

```json
"figure": {
  "file": "G7-1.png",
  "alt": "Figure G7-1: Two-stage RF amplifier schematic with eleven numbered component symbols including transistors, diodes, resistors, capacitors, inductors, and a transformer"
}
```

### `figure` Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | string | Yes | Filename only — no path. File must exist at `figures/{file}` inside the ZIP. |
| `alt` | string | Yes | Descriptive text for accessibility and AI coach context. Should describe what the figure shows in enough detail for someone who cannot see it to reason about the question. |

### Notes

- Multiple questions may reference the same figure file. The app extracts each unique file once.
- `alt` text is injected into the AI coach prompt when the question is presented. Write it descriptively — the coach uses it to reason about diagram-specific questions.
- Omit the `figure` field (or set to `null`) for questions that do not reference a figure. Do not include a `figure` field with an empty `file` string.
- Supported image formats: PNG, JPG/JPEG, GIF, SVG, WebP — any format a modern browser can render in an `<img>` tag.

---

## `preamble` Object

Present when a question requires the student to read a block of reference material before answering — a code listing, class definition, prose description, or mixed content. A preamble may be shared across several consecutive questions by referencing the same file.

This feature was designed for the AP Computer Science question pools, where questions frequently reference Java class definitions and code segments, but the mechanism is subject-agnostic.

Omit this field entirely when not needed — do not write `"preamble": null`.

```json
{
  "id": "APCS1-Q06",
  "subelement": "...",
  "group": "...",
  "question": "What is the output of `getPrice()` when called on a DiningRoomSet with one table priced at 200 and two chairs priced at 50 each?",
  "preamble": {
    "file": "q06-07-dining-room.txt",
    "label": "Table, Chair, and DiningRoomSet class descriptions"
  },
  "answers": { "A": "200", "B": "300", "C": "250", "D": "100", "E": "400" },
  "correct": "B"
}
```

### `preamble` Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | string | Yes | Filename only — no path. File must exist at `preambles/{file}` inside the ZIP. |
| `label` | string | Yes | Short description shown on the collapsible panel header. |

### Notes

- Preamble files are plain text (`.txt`). The full markup convention (backtick, `<code>`, `<table>`) applies.
- Multiple questions may reference the same preamble file. The file is extracted from the ZIP exactly once.
- The preamble is rendered as a collapsible `<details>/<summary>` block positioned above the question text, open by default. The student can collapse it to save screen space.
- The AI coach receives the full preamble text (markup tags stripped) injected into the per-question prompt, regardless of whether the student has the panel open.
- Banks with preambles must be delivered as ZIP archives.

### Relationship to `figure` and `reference_sheet`

| Field | Type | Scope | Rendered as |
|-------|------|-------|-------------|
| `figure` | image file in ZIP | per-question | inline image |
| `preamble` | text file in ZIP | per-question (shareable) | collapsible panel above question |
| `meta.reference_sheet` | inline string in JSON | global (all questions) | modal opened by session-bar button |

These are independent fields. A question may have a figure, a preamble, both, or neither.

---

## `meta.reference_sheet` Field

Some exams provide a reference sheet available to the student for the entire exam — not tied to any individual question. The AP CS A Java Quick Reference is the canonical example.

Stored as a string in `meta`. The full markup convention (`<code>`, backtick) applies to its content.

```json
"meta": {
  ...
  "reference_sheet": "class java.lang.String\n  `int length()`\n  `String substring(int from, int to)`\n  ..."
}
```

**App behaviour:**
- A **"Reference Sheet"** button appears in the session bar when `meta.reference_sheet` is present.
- Clicking the button opens a full-screen modal overlay showing the content rendered with markup support. Clicking outside the panel or the ✕ button dismisses it.
- The reference sheet text is injected (tags stripped) into the AI coach system prompt for every question.

---

## `annotation` Object

Present only when the AI coach needs context it cannot derive from question text alone. Null for the majority of questions.

```json
"annotation": {
  "type": "schematic",
  "content": "Figure G7-1 position 4: symbol shows double-bar cathode (two parallel lines), identifying it as a varactor/varicap diode. Distinguished from zener (bent cathode ends) and rectifier (plain single bar).",
  "errata": null
}
```

### Annotation Types

| Type | Use Case |
|------|----------|
| `schematic` | Figure or circuit diagram described in text for AI reasoning |
| `calculation` | Formula identification and variable mapping for math questions |
| `concept` | Flags a known distractor trap or common misconception |
| `waveform` | Describes a waveform or signal diagram |
| `topology` | Describes a block diagram or system topology |
| `errata` | Question was modified from original pool; describes change |

### `annotation` Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `type` | string | Yes | One of the types above |
| `content` | string | Yes | Context injected to AI coach for this question |
| `errata` | string\|null | No | Description of errata change if applicable |

A question may only have one annotation object. If multiple annotation types apply, use the most specific type and include all context in `content`.

---

## Validation Rules

A valid question bank must satisfy:

1. All required fields present at every level
2. `correct` value exists as a key in `answers`
3. `answers` has 2–6 keys forming a contiguous sequence starting from `A`
4. All `id` values unique within the bank
5. If `structure` present: all `subelement` and `group` values on questions must reference defined IDs
6. No question or answer text may be empty string
7. If `figure` present: both `figure.file` and `figure.alt` must be non-empty strings
8. If any question has a `figure`, the bank must be delivered as a ZIP and `figures/{file}` must exist in the archive
9. If `preamble` present: both `preamble.file` and `preamble.label` must be non-empty strings
10. If any question has a `preamble`, the bank must be delivered as a ZIP and `preambles/{file}` must exist in the archive

---

## Versioning

- Increment minor version (`1.0` → `1.1`) for question corrections, annotation additions, errata
- Increment major version (`1.x` → `2.0`) for pool replacement (new exam cycle)
- Version stored in `meta.version` and should match filename version segment

---

## Example: Minimal Valid Bank (text-only, no structure, no annotations)

```json
{
  "meta": {
    "title": "Sample Test",
    "pool_id": "sample-test-v1",
    "version": "1.0"
  },
  "questions": [
    {
      "id": "Q001",
      "question": "What is the capital of France?",
      "answers": {
        "A": "Berlin",
        "B": "Madrid",
        "C": "Paris",
        "D": "Rome"
      },
      "correct": "C"
    }
  ]
}
```

## Example: Question with Figure (ZIP delivery required)

```json
{
  "id": "G7A09",
  "subelement": "G7",
  "group": "G7A",
  "question": "Which symbol in figure G7-1 represents a field effect transistor?",
  "figure": {
    "file": "G7-1.png",
    "alt": "Figure G7-1: Two-stage RF amplifier schematic with eleven numbered component symbols including transistors, diodes, resistors, capacitors, inductors, and a transformer"
  },
  "answers": {
    "A": "Symbol 2",
    "B": "Symbol 5",
    "C": "Symbol 1",
    "D": "Symbol 4"
  },
  "correct": "C",
  "reference": null,
  "annotation": {
    "type": "schematic",
    "content": "Symbol 1 is an N-channel JFET. Gate arrow points INTO the channel — inward arrow = N-channel. Symbol 2 (NPN BJT) is a bipolar transistor, not a FET.",
    "errata": null
  }
}
```

## Example: Question with Preamble (ZIP delivery required)

```json
{
  "id": "APCS1-Q06",
  "subelement": "APCS1",
  "group": "APCS1-OOP",
  "question": "What is the output of `getPrice()` when called on a `DiningRoomSet` with one table priced at 200 and two chairs priced at 50 each?",
  "preamble": {
    "file": "q06-07-dining-room.txt",
    "label": "Table, Chair, and DiningRoomSet class descriptions"
  },
  "answers": {
    "A": "200",
    "B": "300",
    "C": "250",
    "D": "100",
    "E": "400"
  },
  "correct": "B",
  "reference": null,
  "annotation": null
}
```

The corresponding ZIP structure:
```
bank.json
figures/
  G7-1.png
preambles/
  q06-07-dining-room.txt
  q12-13-insert-sort.txt
```

---

*Schema version: 1.2 — adds `preamble` field, `meta.reference_sheet`, variable answer count (2–6), and full markup convention (backtick inline code, `<code>` block, `<table>` tag).*
