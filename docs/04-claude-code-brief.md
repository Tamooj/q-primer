# Claude Code Implementation Brief
## Q-Primer — v1.0

---

## What You Are Building

A single-file browser application (`q-primer.html`) that helps students study for multiple-choice exams using an AI coach powered by the Anthropic API. No server, no build step, no framework dependencies.

Read these specs in full before writing any code:
- `01-question-bank-schema.md` — JSON format for question banks
- `02-app-architecture.md` — component breakdown, state schema, module interfaces
- `03-prompt-design.md` — exact prompt templates and API call structure

---

## Deliverables

1. `app/q-primer.html` — complete working application
2. `banks/ham-general-2023-2027-v1.1.json` — ham radio general class question bank, converted from source markdown
3. `README.md` — user setup guide
4. `spec/bank-template.json` — minimal example bank for contributors

---

## Implementation Order

Build in this sequence. Each step should be independently testable before moving to the next.

### Step 1: Static scaffold
- HTML structure with Setup Panel and Study View (Study View hidden)
- CSS — see UI Design section below
- No JS yet
- Verify layout renders correctly

### Step 2: BankLoader
- File input that accepts JSON
- Parse and validate against schema (required fields, answer key integrity, no duplicate IDs)
- On success: store bank in memory, display bank title and question count
- On failure: display specific validation error
- Test with `spec/bank-template.json` and a deliberately malformed file

### Step 3: Setup flow
- API key input field (type=password)
- Store key in sessionStorage on entry
- Student profile textarea (stored in localStorage under `q-primer:student`)
- "Start Studying" button — enabled only when both bank loaded and key present
- Transition to STUDY state on button click

### Step 4: SessionState
- Initialize session object on STUDY state entry
- Persist to localStorage on every mutation
- Expose: `getSession()`, `recordAnswer(id, choice, correct)`, `recordSkip(id)`, `updateTokenUsage(input, output)`

### Step 5: QuizEngine
- `getNextQuestion(bank, session)` — returns next question object, randomized, excluding already-answered
- Fisher-Yates shuffle, run once per session on bank load, order stored in session
- Filter support: by subelement, by group, or full pool (full pool only in v1 UI, filter infrastructure ready)
- `isSessionComplete(bank, session)` — returns true when all questions answered or skipped

### Step 6: Question Panel rendering
- Display question text and A–D answer choices from bank verbatim
- Four answer buttons
- Submit button (enabled after choice selected) and Skip button
- On submit: reveal correct answer, highlight correct (green) and student choice if wrong (red)
- Display question ID and reference if present
- "Next Question" button appears after answer revealed

### Step 7: CoachAPI
- `callCoach(apiKey, systemPrompt, messages)` — fetch call to `api.anthropic.com/v1/messages`
- Returns `{ text, inputTokens, outputTokens }` on success
- Returns `{ error, status }` on failure
- See prompt spec for exact API call parameters

### Step 8: PromptBuilder
- `buildSystemPrompt(meta, studentProfile)` — see prompt spec template
- `buildPostAnswer(question, studentChoice, sessionContext)` — see prompt spec template
- `buildPreExplain(question)` — see prompt spec template
- Unit-testable: each function takes plain objects and returns a string

### Step 9: Coach Panel
- Triggered automatically after student submits answer
- Show loading state while API call in flight
- Render coach response (markdown → HTML, basic: bold, italic, paragraphs, code blocks)
- Show token usage for this call and session running total
- "Ask a follow-up" text input for continued dialog on current question
- Follow-up appends to messages array and calls coach again

### Step 10: Session Bar
- Running score: X correct / Y answered (Z%)
- Questions remaining count
- "End Session" button → returns to SETUP state, clears session from localStorage

### Step 11: Bank conversion
- Convert `ham_general_2023_2027.md` to `ham-general-2023-2027-v1.1.json`
- Parse question ID headings for ID and correct answer letter
- Parse reference codes from brackets
- Parse question text and A–D answers
- Parse and preserve annotation comments where present
- Map subelement and group structure
- Validate output against schema before committing

---

## UI Design

The aesthetic should feel like a focused study tool — clean, functional, slightly technical. Not clinical, not playful. Think: a well-designed terminal interface that grew up.

**Color palette:**
- Background: `#0f1117` (near-black, slight blue)
- Surface: `#1a1d27`
- Border: `#2e3347`
- Accent: `#4a9eff` (clear blue)
- Correct: `#22c55e`
- Incorrect: `#ef4444`
- Text primary: `#e8eaf0`
- Text secondary: `#8b90a7`

**Typography:**
- UI chrome: `'IBM Plex Mono', monospace` — reinforces technical/radio feel
- Question text: `'IBM Plex Sans', sans-serif` — readable for longer text
- Both available from Google Fonts

**Layout:**
- Two-column on desktop: Question Panel (left, 55%) / Coach Panel (right, 45%)
- Single column on mobile, Coach Panel below
- Session Bar fixed at top, slim
- Setup Panel centered, max-width 480px

**Question Panel:**
- Question text large and clear, generous line height
- Answer buttons full-width, left-aligned text, clear hover state
- Selected answer has distinct border highlight before submission
- After submission: correct answer gets green background, wrong student choice gets red background, other choices dim

**Coach Panel:**
- Scrollable, independent of question panel scroll
- Loading state: subtle animated pulse, not a spinner
- Token count displayed small, bottom of panel, secondary text color
- Follow-up input pinned to bottom of coach panel

**Micro-interactions:**
- Answer button selection: immediate visual feedback, no delay
- Submit → result reveal: brief 200ms transition on answer highlighting
- Coach response: fade in, not pop in
- "Next Question" button: appears with a subtle slide-up after result revealed

---

## Specific Implementation Requirements

### Security
- API key: `sessionStorage` only, never `localStorage`, never logged to console
- Bank JSON: parsed with `JSON.parse()` only, no `eval()`
- All dynamic text inserted as `textContent` or via a safe markdown renderer — never raw `innerHTML` with user content

### API key input
- `type="password"` input
- After entry and session start, the key is not displayed again
- If API call returns 401, prompt user to re-enter key (sessionStorage may have stale value)

### Markdown rendering in coach panel
Implement a minimal safe renderer supporting:
- `**bold**`
- `*italic*`
- `` `inline code` ``
- ` ```code blocks``` `
- Paragraph breaks
- No external markdown library required — 40 lines of regex is sufficient for this use case

### Question randomization
- Fisher-Yates shuffle run once when session starts
- Shuffle order stored in `session.questionOrder` array
- Same session always presents questions in same order (reproducible)
- New session gets new shuffle

### Error states to handle explicitly
- Bank file is not valid JSON
- Bank file is valid JSON but fails schema validation (report which field)
- API key missing when coach panel is triggered (prompt to enter key)
- API call fails (display error in coach panel, do not lose question state)
- All questions answered (show completion screen with final score)

---

## Bank Conversion Notes (ham-general-2023-2027-v1.1.json)

Source file: `ham_general_2023_2027.md`

Parsing rules:
- Question ID and correct answer: `#### G1A01 (C) [97.301(d)]` → id=`G1A01`, correct=`C`, reference=`97.301(d)`
- Question text: paragraph immediately following the ID heading
- Answers: lines beginning with `A.`, `B.`, `C.`, `D.` — strip the prefix, trim whitespace
- Section separator: `---`
- Annotations: lines matching `<!-- SCHEMATIC: -->`, `<!-- CONCEPT: -->`, `<!-- CALCULATION: -->`, `<!-- WAVEFORM: -->`, `<!-- TOPOLOGY: -->` — strip comment markers, preserve content
- Deleted questions (marked in errata): exclude from output
- Errata corrections: apply corrections to question/answer text before output — the JSON represents the corrected pool

Subelement structure: parse from the `## SUBELEMENT G1 –` headings and `### G1A –` group headings.

The conversion script does not need to be included in the app. It is a one-time ETL. Output the final JSON only.

---

## README Content Requirements

The README must cover:
1. What Q-Primer is (one paragraph)
2. How to get an Anthropic API key (step by step, with link to console.anthropic.com)
3. How to run the app (open the HTML file — that's it)
4. How to use it (load a bank, enter key, enter profile, start studying)
5. Available question banks (list with links)
6. How to contribute a question bank (format reference, link to spec)
7. License

---

## Definition of Done

- [ ] App loads in browser with no console errors
- [ ] Bank loads and validates correctly with ham JSON
- [ ] Invalid bank file shows specific error message
- [ ] Quiz flow: question renders verbatim, answer submits, result reveals, coach explains
- [ ] Follow-up question dialog works
- [ ] Token usage accumulates correctly across calls
- [ ] Session score tracks correctly
- [ ] Student profile persists across browser refresh
- [ ] API key clears on tab close (sessionStorage)
- [ ] API errors display in coach panel without losing question state
- [ ] Session completes gracefully when all questions answered
- [ ] Renders correctly on mobile (single column)
- [ ] Ham general JSON validates against schema
- [ ] README complete
