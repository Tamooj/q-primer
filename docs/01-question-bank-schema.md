# Question Bank Schema Specification
## Q-Primer — v1.0

---

## Overview

A question bank is a single JSON file that fully describes a multiple-choice test pool. The app treats the file as a pure data dependency — it contains no subject-specific logic. The app never generates, infers, or modifies question content.

Question banks are portable, versionable, and human-readable. They may be loaded from local file upload or (future) remote URL.

---

## File Naming Convention

```
{subject-slug}-{pool-id}-{version}.json
```

Examples:
- `ham-general-2023-2027-v1.1.json`
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
| `answers` | object | Yes | Keys must be `A`, `B`, `C`, `D`. All four required. |
| `correct` | string | Yes | Must be `A`, `B`, `C`, or `D`. |
| `reference` | string | No | Rule citation, chapter reference, etc. Displayed in UI. |
| `annotation` | object\|null | No | See Annotation schema below. |

### Answer Key Rules

- `correct` is the **sole authoritative source** for the correct answer
- The app must never derive or infer the correct answer from any other field
- Answer text must be stored verbatim — no reformatting, no punctuation normalization

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
3. `answers` contains exactly the keys `A`, `B`, `C`, `D`
4. All `id` values unique within the bank
5. If `structure` present: all `subelement` and `group` values on questions must reference defined IDs
6. No question or answer text may be empty string

---

## Versioning

- Increment minor version (`1.0` → `1.1`) for question corrections, annotation additions, errata
- Increment major version (`1.x` → `2.0`) for pool replacement (new exam cycle)
- Version stored in `meta.version` and should match filename version segment

---

## Example: Minimal Valid Bank (3 questions, no structure, no annotations)

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

---

*Next: `02-app-architecture.md`*
