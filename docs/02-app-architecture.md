# Application Architecture Specification
## Q-Primer — v1.0

---

## Overview

Q-Primer is a single-file browser application. No server, no build step, no installation. The user opens one HTML file (or a hosted URL) and it runs entirely in their browser.

All persistent state lives in `localStorage`. All API calls go directly from the browser to `api.anthropic.com`. No data passes through any intermediate server.

---

## Technology Constraints

- **Single HTML file** — HTML + CSS + JS, no bundler, no framework dependencies
- **No backend** — zero server components in v1
- **External dependencies** — loaded from CDN only, pinned versions
  - No required dependencies beyond vanilla JS for v1
- **Browser support** — modern evergreen browsers only (Chrome, Firefox, Safari, Edge)
- **No localStorage for API key** — API key stored in `sessionStorage` only (cleared on tab close)

---

## Component Map

```
┌─────────────────────────────────────────────────────┐
│  App Shell                                          │
│  ┌──────────────┐  ┌─────────────────────────────┐ │
│  │  Setup Panel │  │  Study View                 │ │
│  │              │  │  ┌───────────────────────┐  │ │
│  │  - API key   │  │  │  Question Panel       │  │ │
│  │  - Bank load │  │  │  - Question text      │  │ │
│  │  - Profile   │  │  │  - Answer choices     │  │ │
│  │              │  │  │  - Submit / Skip      │  │ │
│  └──────────────┘  │  │  - Result reveal      │  │ │
│                    │  └───────────────────────┘  │ │
│                    │  ┌───────────────────────┐  │ │
│                    │  │  Coach Panel          │  │ │
│                    │  │  - AI response        │  │ │
│                    │  │  - Explain button     │  │ │
│                    │  │  - Token usage        │  │ │
│                    │  └───────────────────────┘  │ │
│                    │  ┌───────────────────────┐  │ │
│                    │  │  Session Bar          │  │ │
│                    │  │  - Score              │  │ │
│                    │  │  - Progress           │  │ │
│                    │  │  - Filter controls    │  │ │
│                    │  └───────────────────────┘  │ │
│                    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Application States

The app exists in one of three top-level states. State transitions are explicit.

```
SETUP ──── bank loaded + key entered ──→ STUDY
STUDY ──── session end / new bank ──────→ SETUP
SETUP ──── (future) restore session ───→ STUDY
```

### SETUP state
User has not yet provided a valid API key and loaded a question bank. Setup Panel is shown. Study View is hidden.

### STUDY state
API key present in sessionStorage, question bank loaded in memory. Setup Panel is hidden. Study View is shown.

---

## Module Breakdown

Each module is a self-contained JS object or set of functions. No module reaches into another module's internal state — all communication through defined interfaces.

### `BankLoader`
Responsibilities:
- Accept file upload (JSON)
- Parse and validate against schema
- Return a validated bank object or a structured error

Does not: store state, touch the DOM, make API calls.

### `SessionState`
Responsibilities:
- Maintain current session object (see State Schema below)
- Persist session to localStorage on every update
- Expose read/write interface to all other modules
- Load existing session from localStorage on init

Does not: make API calls, touch the DOM.

### `QuizEngine`
Responsibilities:
- Select next question based on current filter and session state
- Randomize question order (Fisher-Yates, seeded per session)
- Track answered/wrong/skipped
- Determine when a session or filtered subset is complete

Does not: render anything, make API calls.

### `PromptBuilder`
Responsibilities:
- Construct the system prompt from student profile + bank metadata
- Construct the per-question user message from question object + student answer + result
- Inject annotation content when present
- Return complete messages array ready for API call

Does not: make API calls, touch the DOM, hold state.
This is the **single point of control** for what context gets sent to the API.

### `CoachAPI`
Responsibilities:
- Accept a messages array from PromptBuilder
- Make the fetch call to `api.anthropic.com/v1/messages`
- Return response text and usage stats
- Handle errors (auth failure, rate limit, network) and return structured error objects

Does not: construct prompts, touch the DOM, hold state.

### `UI`
Responsibilities:
- Render all DOM elements
- Handle all user input events
- Call other modules in response to user actions
- Display coach responses, scores, token usage

Does not: hold application state (reads from SessionState), construct prompts, make API calls directly.

---

## State Schema

The session state object. V1 writes a subset of fields. Schema defined now so future additions are additive only.

```json
{
  "session": {
    "id": "uuid-v4",
    "bank_id": "ham-general-2023-2027-v1.1",
    "started_at": "2026-05-09T14:00:00Z",
    "last_active": "2026-05-09T15:30:00Z",
    "filter": {
      "subelement": null,
      "group": null,
      "mode": "random"
    },
    "progress": {
      "answered": ["G1A01", "G3B04"],
      "correct": ["G1A01"],
      "wrong": ["G3B04"],
      "skipped": []
    },
    "token_usage": {
      "session_input": 4820,
      "session_output": 1203,
      "session_total": 6023
    }
  },
  "student": {
    "profile": "I have a Masters in EE with 10 years RF engineering experience. I understand circuit theory and transmission line math. I need depth on regulations and operating procedures, not electronics fundamentals.",
    "created_at": "2026-05-09T14:00:00Z"
  },
  "coach_context": {
    "session_summary": null
  }
}
```

### V1 fields actively used
- `session.id`, `session.bank_id`, `session.started_at`, `session.last_active`
- `session.filter`
- `session.progress`
- `session.token_usage`
- `student.profile`

### Deferred fields (schema present, not populated in v1)
- `coach_context.session_summary` — reserved for cross-session continuity feature

---

## API Call Construction

`PromptBuilder` produces this structure for every coach interaction.

### System Prompt

```
You are a study coach helping a student prepare for a multiple-choice exam.

Bank: {meta.title} — {meta.description}

Student profile: {student.profile}

Your role:
- When shown a question, the student's answer, and the correct answer, explain why the correct answer is right and why the wrong answers are wrong.
- Calibrate explanation depth and examples to the student's stated background.
- Be concise unless the student asks to go deeper.
- Never reveal the correct answer before the student has answered.
- Use real-world examples relevant to the student's background when helpful.
```

### User Message (post-answer)

```
Question ID: {id}
Reference: {reference}

Question: {question}

A. {answers.A}
B. {answers.B}
C. {answers.C}
D. {answers.D}

Student answered: {student_choice}
Correct answer: {correct}
Result: {correct|incorrect}

{if annotation} Context for your explanation: {annotation.content} {/if}

Please explain why {correct} is correct and address why the other choices are wrong.
```

### Pre-answer (explain on demand only)
If the student requests explanation before answering, correct answer is withheld from the message. The `PromptBuilder` has two message construction paths: `buildPostAnswer()` and `buildPreExplain()`. The correct answer field is only included in `buildPostAnswer()`.

---

## Token Usage Display

Every API response includes a `usage` object:
```json
{ "input_tokens": 412, "output_tokens": 287 }
```

The app accumulates these in `session.token_usage` and displays a running total in the UI. No balance query to the API — not supported. On `401` or `403` response, display: *"API key issue — check your Anthropic console at console.anthropic.com"*

---

## localStorage Key Structure

```
q-primer:session        — current session object (full state schema)
q-primer:student        — student profile object
q-primer:bank:{pool_id} — cached bank JSON (future, not v1)
```

Keys are namespaced to avoid collisions with other apps.

`sessionStorage` key:
```
q-primer:apikey         — API key, cleared on tab close
```

---

## Security Notes

- API key is never written to `localStorage`, only `sessionStorage`
- API key is never logged, never displayed after entry (input type=password)
- No analytics, no telemetry, no external calls except `api.anthropic.com`
- Question bank JSON is parsed with `JSON.parse()` — no `eval()`
- All user-provided text rendered as textContent, not innerHTML

---

## File Structure (delivered artifact)

```
q-primer.html           — complete application, single file
```

For the repo:
```
/app/q-primer.html      — application
/banks/                   — published question banks
/spec/                    — this document and schema spec
/etl/                     — (future) conversion tools
/README.md                — setup and usage guide
```

---

*Next: `03-prompt-design.md`*
