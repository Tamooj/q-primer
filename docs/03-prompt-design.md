# Prompt Design Specification
## Q-Primer — v1.0

---

## Overview

The prompt layer is the interface between the app and the AI coach. It is entirely owned by `PromptBuilder`. No other module constructs or modifies prompts.

The central discipline: **the AI coach never generates question content**. It only receives question content as context and responds to it. This is enforced structurally — question text and answer choices flow into the prompt as literal injected strings, not as instructions to the model.

---

## System Prompt

Constructed once per session. Injected as the `system` field on every API call.

### Template

```
You are a study coach helping a student prepare for a multiple-choice examination.

EXAM CONTEXT
Title: {{meta.title}}
{{#if meta.subtitle}}Subtitle: {{meta.subtitle}}{{/if}}
{{#if meta.description}}About this exam: {{meta.description}}{{/if}}
{{#if meta.exam_question_count}}The actual exam draws {{meta.exam_question_count}} questions from this pool.{{/if}}
{{#if meta.passing_score}}Passing score: {{meta.passing_score}} correct out of {{meta.exam_question_count}}.{{/if}}

STUDENT PROFILE
{{#if student.profile}}
{{student.profile}}
{{else}}
No profile provided. Assume a motivated adult learner with no specific background information.
{{/if}}

YOUR ROLE
- Explain why the correct answer is correct and why each wrong answer is wrong.
- Calibrate depth, vocabulary, and examples to the student's stated background. Do not explain concepts they already know unless asked.
- Be concise by default. Go deeper only if the student asks.
- Use real-world examples relevant to the student's background when they would genuinely help.
- Never reveal the correct answer before the student has submitted their response.
- When a student gets something wrong, be direct about why — do not soften the explanation to the point of vagueness.

CONSTRAINTS
- Do not rewrite, paraphrase, or modify question text or answer choices in your responses.
- Do not generate new practice questions.
- Do not speculate about the correct answer — it will always be provided to you after the student answers.
```

### Notes

- `{{meta.description}}` is the primary signal to the coach about subject matter context
- Student profile is free text — no parsing, no structure assumed
- If profile is absent, the fallback instruction prevents the coach from over-explaining or under-explaining by default
- The "do not rewrite question text" constraint is critical — it prevents the coach from inadvertently introducing confusion by quoting a paraphrased version

---

## User Messages

Two construction paths. Both are called by `PromptBuilder` methods.

---

### Path 1: `buildPostAnswer(question, studentChoice, sessionContext)`

Called after the student submits their answer. This is the primary interaction path.

**Parameters:**
- `question` — full question object from bank
- `studentChoice` — `"A"` | `"B"` | `"C"` | `"D"`
- `sessionContext` — object with `{ wrongCount }` (times student has gotten this question wrong this session)

**Output message:**

```
QUESTION {{question.id}}{{#if question.reference}} [{{question.reference}}]{{/if}}

{{question.question}}

A. {{question.answers.A}}
B. {{question.answers.B}}
C. {{question.answers.C}}
D. {{question.answers.D}}

Student answered: {{studentChoice}}
Correct answer: {{question.correct}}
Result: {{#if correct}}CORRECT{{else}}INCORRECT{{/if}}

{{#if question.annotation}}
CONTEXT FOR YOUR EXPLANATION
{{question.annotation.content}}
{{/if}}

{{#if incorrect}}
{{#if sessionContext.wrongCount > 1}}
Note: This student has answered this question incorrectly before. Consider a different angle or a more fundamental explanation.
{{/if}}
{{/if}}

Explain why {{question.correct}} is correct. Address why each wrong answer is wrong, briefly.
```

**Key rules:**
- `question.correct` is always included in this message — the student has already answered
- Annotation content is injected only when `question.annotation` is non-null
- The repeat-wrong note is only added when `wrongCount > 1` — not on first wrong answer

---

### Path 2: `buildPreExplain(question)`

Called only when a student explicitly requests explanation *before* answering (on-demand, not automatic). Less common path.

**Output message:**

```
QUESTION {{question.id}}{{#if question.reference}} [{{question.reference}}]{{/if}}

{{question.question}}

A. {{question.answers.A}}
B. {{question.answers.B}}
C. {{question.answers.C}}
D. {{question.answers.D}}

The student has not yet answered. Do not reveal the correct answer.

Explain the concept being tested by this question without indicating which answer is correct. Help the student reason toward the answer.
```

**Key rules:**
- `question.correct` is **never** included in this message
- The instruction "do not reveal" is explicit and in both the system prompt and the user message (belt and suspenders)

---

## Conversation History

The API is stateless. Each call includes conversation history for the current question exchange only.

### Standard exchange structure (messages array):

```json
[
  {
    "role": "user",
    "content": "<buildPostAnswer output>"
  }
]
```

Single-turn for the primary path. The coach responds once per question.

### Follow-up questions

If the student asks a follow-up question after the coach's initial explanation, the app appends to the messages array:

```json
[
  { "role": "user", "content": "<buildPostAnswer output>" },
  { "role": "assistant", "content": "<coach first response>" },
  { "role": "user", "content": "<student follow-up question>" }
]
```

This continues until the student moves to the next question, at which point history is discarded. Question-scoped history only — no cross-question conversation threading in v1.

---

## API Call Parameters

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "system": "<system prompt>",
  "messages": [...]
}
```

### Parameter rationale

- `max_tokens: 1024` — sufficient for thorough explanations; prevents runaway responses
- Model is hardcoded to current Sonnet — not user-configurable in v1
- No `temperature` override — default is appropriate for explanatory content

---

## Error Handling

`CoachAPI` returns structured errors. `UI` maps them to user-facing messages.

| HTTP Status | Meaning | User Message |
|-------------|---------|--------------|
| 401 | Invalid API key | "API key not recognized. Check your key at console.anthropic.com" |
| 403 | Permission denied | "API key doesn't have permission. Check your Anthropic account." |
| 429 | Rate limited | "Too many requests. Wait a moment and try again." |
| 529 | API overloaded | "Anthropic's API is busy. Try again in a moment." |
| Network error | No connectivity | "Can't reach Anthropic's API. Check your connection." |

All errors are displayed in the Coach Panel where the response would appear. The question state is preserved — the student can retry without losing their answer.

---

## What the Coach Is Never Asked To Do

These are explicit non-uses enforced by PromptBuilder's construction logic:

- Generate new questions or answer choices
- Determine the correct answer (always provided from bank)
- Summarize session performance (handled by app logic in v1)
- Produce the question text for display (app renders directly from bank)
- Score the student (app logic)

---

*Next: `04-claude-code-brief.md`*
