# Question Bank Schema Specification
## Q-Primer — v1.1

---

## Overview

A question bank is a single JSON file that fully describes a multiple-choice test pool. The app treats the file as a pure data dependency — it contains no subject-specific logic. The app never generates, infers, or modifies question content.

Question banks are portable, versionable, and human-readable. They may be loaded from local file upload or from a remote URL.

---

## Delivery Format

Question banks come in two forms:

**Plain JSON (`.json`)** — text-only banks with no figures. A single file containing the full schema.

**ZIP archive (`.zip`)** — banks whose questions reference figures (diagrams, schematics, charts). The ZIP must contain:
```
bank.json          — the question bank (full schema, required)
figures/           — directory of image files (PNG, JPG, or other browser-renderable formats)
  G7-1.png
  G3-1.jpg
  ...
```
`bank.json` references figure files by filename only (not path). The app looks for them under `figures/` inside the ZIP. Every filename referenced in a question's `figure.file` field must exist in `figures/`; the build script (`construction/build-bank.py`) enforces this.

The app deduplicates figures automatically: multiple questions may reference the same file; the image is extracted from the ZIP exactly once.

---

## File Naming Convention

```
{subject-slug}-{pool-id}-{version}.json    (plain JSON)
{pool-id}.zip                              (ZIP with figures)
```

Examples:
- `ham-general-2023-2027-v1.1.json`
- `fcc-element3-2023-2027-sample.zip`
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
  "version": "1.1",
  "effective_from": "2023-07-01",
  "effective_to": "2027-06-30",
  "total_questions": 429,
  "passing_score": 26,
  "exam_question_count": 35,
  "source_url": "https://www.arrl.org/general-class-question-pool",
  "description": "Official FCC question pool for the Amateur Radio General Class license examination.",
  "tags": ["amateur radio", "FCC", "RF", "electronics"]
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
| `question` | string | Yes | Verbatim question text. Never modified by app. |
| `answers` | object | Yes | 2–6 keys forming a contiguous sequence from `A` (e.g. `A,B` or `A,B,C,D` or `A`–`F`). All values must be non-empty strings. |
| `correct` | string | Yes | Must be one of the keys present in `answers`. |
| `reference` | string | No | Rule citation, chapter reference, etc. Displayed in UI. |
| `figure` | object\|null | No | See Figure schema below. Required for questions that reference a diagram. |
| `annotation` | object\|null | No | See Annotation schema below. |

### Answer Key Rules

- `correct` is the **sole authoritative source** for the correct answer
- The app must never derive or infer the correct answer from any other field
- Answer text must be stored verbatim — no reformatting, no punctuation normalization
- Keys must be a **contiguous sequence starting from `A`**: valid sets are `{A,B}`, `{A,B,C}`, `{A,B,C,D}`, `{A,B,C,D,E}`, `{A,B,C,D,E,F}`. Gaps are not allowed (e.g. `{A,C}` is invalid).
- Traditional 4-choice (`A`–`D`) is the default; use fewer or more only when the source material genuinely warrants it

---

## Markup Convention (question text, answer text, preamble files, reference_sheet)

Three constructs are supported everywhere text is displayed. All rendering is
DOM-safe — `textContent` only, never `innerHTML`.

| Construct | Syntax | Renders as |
|-----------|--------|------------|
| Inline code | `` `identifier` `` | Monospace inline span — preferred for class/variable names |
| Inline code (tag form) | `<code>expr</code>` | Same monospace span — still supported |
| Block code | `<code>\n...\n</code>` | `<pre><code>` scrollable block — content has newlines |
| Table | `<table>\n...\n</table>` | HTML table — pipe-delimited rows, first row is header |

Any other HTML-like tag in these fields is rendered as literal text.

See `docs/07-preamble-feature.md` for full examples including mixed prose/code
preambles and the table format for AP CS-style answer matrices.

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

The corresponding ZIP structure:
```
bank.json
figures/
  G7-1.png
```

---

*Next: `02-app-architecture.md`*
