# Deferred Features
## Q-Primer — Post-v1 Backlog

These features were deliberately excluded from v1 scope. Architecture decisions in v1 were made to keep these additions non-breaking. This document records intent so future contributors don't treat them as surprises.

---

## Session Continuity

**What:** Compressed AI-generated session summary persisted to localStorage. On session resume, the summary is injected into the system prompt so the coach picks up context from prior sessions.

**Why deferred:** Requires a summary-generation API call at session end. Adds complexity to session restore flow. Not needed for the core study experience.

**Architectural hook:** `session.coach_context.session_summary` field exists in state schema, null in v1. `PromptBuilder.buildSystemPrompt()` already accepts this field — when non-null, append to system prompt. Implementation is additive.

---

## Question-Relevant History Injection

**What:** When loading a question, query session history for prior attempts on this question and related topic. Inject a filtered slice into the user message (e.g., "student has gotten this question wrong twice; struggled with MUF/LUF in G3B generally").

**Why deferred:** Requires a local query layer over session history. Session history schema supports it — progress tracking is already per-question-ID.

**Architectural hook:** `PromptBuilder.buildPostAnswer()` accepts a `sessionContext` parameter. V1 only passes `wrongCount`. Future versions pass richer context from a `SessionQuery` module.

---

## ~~Remote Bank Loading~~ *(shipped)*

URL loading is implemented. `BankLoader.loadFromUrl(url)` fetches a bank by URL, normalises Google Drive share links, and dispatches to JSON or ZIP processing. The last-used URL is persisted to `localStorage` and auto-reloaded on page open.

A bank discovery / browser UI is still deferred.

---

## Topic/Subelement Filtering UI

**What:** UI controls to filter quiz to a specific subelement or group. "Quiz me on G3 only."

**Why deferred:** QuizEngine filter infrastructure is built. `session.filter` schema is defined. V1 just doesn't expose filter controls in the UI.

**Architectural hook:** Add filter controls to Session Bar. Pass filter to `QuizEngine.getNextQuestion()`. No other changes needed.

---

## Drill Mode

**What:** Re-quiz wrong answers from the session. Separate mode triggered explicitly.

**Why deferred:** Session progress tracking (correct/wrong/skipped per ID) is fully implemented in v1. Drill mode is a QuizEngine filter over `session.progress.wrong`.

**Architectural hook:** Add "Drill weak areas" button. `QuizEngine.getDrillQuestion(bank, session)` — draw from `session.progress.wrong` only.

---

## Export / Import Session State

**What:** Export session state as JSON file. Import on another device. Enables cross-device continuity and teacher-to-student profile sharing.

**Why deferred:** Session state schema is stable and complete. Export is `JSON.stringify(localStorage.getItem('q-primer:session'))`. Import is the reverse with validation.

---

## ETL Tooling

**What:** Browser-based or CLI tools to convert common source formats (PDF, Word, CSV, existing markdown pools) into the Q-Primer JSON schema.

**Why deferred:** One-time per bank. The ham general bank is already converted. Future banks can be converted manually or with ad-hoc scripts until there's enough volume to justify a tool.

**Architectural hook:** `spec/01-question-bank-schema.md` is the conversion target spec. ETL tools live in `/etl/` directory.

---

## Multi-Model Support

**What:** Allow users to plug in an OpenAI key and use GPT-4o as the coach instead of Claude.

**Why deferred:** `CoachAPI` module is isolated — all API calls go through one function. Adding an OpenAI adapter means implementing `CoachAPI.callOpenAI()` and adding a model selector to Setup.

**Note:** Deferred intentionally. Q-Primer is currently Anthropic-only by design choice.

---

## Teacher / Classroom Features

**What:** Pre-populated student profiles distributed by teachers. Class-level progress tracking. Shared session export.

**Why deferred:** Requires either a server component or a peer-to-peer sharing mechanism. Out of scope for a client-only v1.

---

## Token Budget Warning

**What:** Warn user when session token usage approaches a threshold they set. Useful for users on limited API credits.

**Why deferred:** Token tracking is fully implemented in v1. This is a UI addition: a settings field for budget threshold, a warning state in the Session Bar.
