# Q-Primer  ("Que-Prĭmmer")


**An AI-coached study tool for multiple-choice exam preparation.**

Q-Primer is a free, open-source study tool that helps people prepare for multiple-choice examinations by combining quiz practice with an AI-powered coaching conversation. The quize tool runs locally and entirely in your web browser — no software to install, no server required. The optional AI coach makes API calls to Anthropics API using the users API key.  The free tier account should be sufficient; a study session typically costs a few penny's at most. To use this, a student opens a single webpage, loads a set of practice questions, and starts studying.

---

## Getting Started

Q-Primer requires no installation, no server, and no build step. It is a single HTML file that runs entirely in your browser.

**1. Get the files**

Download the index.html and a quiz file (in /banks), or clone the whole repository:
```
git clone https://github.com/Tamooj/q-primer.git
```
Or use the GitHub **Code → Download ZIP** button and extract it anywhere on your computer.

**2. Open the app**

Open `index.html` directly in any modern browser (Chrome, Firefox, Edge, or Safari). You can do this by double-clicking the file in your file manager, or by dragging it into a browser window. While a little space constrained, this should work just fine on most mobile devices too.

Alternatively, the app is hosted on GitHub Pages at **https://tamooj.github.io/q-primer/** — and can be opened directly from there in your browser (no download required).

**3. Load a question bank**

Either drag a question bank file from the `banks/` folder onto the drop zone, or paste a direct URL into the URL field and click Load. They quizes .zip files that  basically just a single .json of questions/answers, but the zip file allows the inclusion of figure images, which are needed by some quizes)
There are a few sample quizzes provided for practice.  Feel free to submit your own - the file format is is described in the docs, and a simple assembly pythjon script is provided.  Banks loaded by URL are remembered locally and reloaded automatically on your next visit to save on typing.

**4. Start studying**

Enter your name and some background about you to help the AI coach give advice appropriate to your skillset (optional), add an API key if you have one, and click **Start Studying**. You have the option to get quiz question in sequential or random order. Your progress is saved automatically in your browser cache and will be waiting when you return.  

---

## Prerequisites

**To use the AI coaching features, you will need an Anthropic API key.**

Q-Primer calls Anthropic's Claude API directly from your browser; there is no intermediary server. You provide your own API key, which means your usage is billed to your own Anthropic account. A free-tier API key is typically sufficient to get started; study sessions typically cost a few cents worth of token each.

The quiz itself — loading a question bank, answering questions, and seeing correct/incorrect feedback — works without an API key. The AI coach explanation that appears after each answer is what requires the API key.

Instructions for obtaining an API key will be included in the full setup guide. The short version: create an account at [console.anthropic.com](https://console.anthropic.com), navigate to API Keys, and generate a key. Paste it into the app. By default the key is held only in your browser tab (cleared when you close it); check **Remember this key** to save it to `localStorage` so it persists across sessions on your device.

---

## How It Works

Practice questions come from a **question bank** — a structured file containing the complete pool of questions for a given exam, including all four answer choices and the correct answer for each. Question banks are plain text files in a documented format, which means teachers, subject matter experts, and community volunteers can create and share them.

When a student answers a question, an AI coach (Anthropic's Claude) explains why the correct answer is correct, why each wrong answer is wrong, and engages in follow-up conversation if the student wants to go deeper. Critically, **the AI never generates the questions** — it only explains them. The question bank is the authoritative source; the AI is just the tutor.

The coach calibrates its explanations to a **student profile**: a short free-text description of the student's background and goals. A retired engineer studying ham radio regulations gets different explanations than a seventh-grader studying AP Computer Science. This profile is written by the student (or pre-populated by a teacher).

---

## Current Status

**Q-Primer is working and available for testing.** The core application is built and functional: question banks load, the quiz loop runs, session progress persists across page reloads, and the AI coach is live. We are actively seeking educator feedback to shape ongoing development.

To try it: open [`index.html`](index.html) in any modern browser, load a question bank from [`/banks`](banks/), and start studying. An API key is optional — the quiz works without one; coaching requires it.

The specification documents in [`/docs`](docs/) describe the intended behavior in detail, including explicit questions for educator review. The most relevant document for non-technical reviewers is:

→ **[`docs/06-use-cases-and-user-stories.md`](docs/06-use-cases-and-user-stories.md)** — Describes the intended users, what they need from the tool, and the open pedagogical questions we are asking educators to weigh in on.

We are particularly interested in perspectives from:
- **Classroom teachers** who create their own practice materials and want tools that align to their curriculum
- **Tutors** working with adult learners preparing for high-stakes exams (GRE, professional certifications, licensing exams)
- **Subject matter experts** who maintain official question pools and administer exams (e.g., Volunteer Examiners for amateur radio licensing)
- **Learning science researchers** with views on feedback timing, spaced repetition, and AI's role in formative assessment

---

## The Core Pedagogical Questions

These are the questions we are least confident about. We would value your experience and expertise on any of them.

**1. Immediate vs. delayed feedback**
Q-Primer reveals the correct answer immediately after the student submits. Some research suggests delayed feedback produces better long-term retention. Should this be configurable? Does the answer differ for exam prep versus conceptual learning?

**2. Explanation before vs. after answering**
Questions are currently presented cold — no scaffolding before the student commits to an answer. An on-demand "explain before I answer" path exists but is not the default. Is cold presentation the right default for exam prep? Are there question types where pre-answer scaffolding should be standard?

**3. Wrong answers and the hypercorrection effect**
Research suggests confidently-wrong answers, once corrected, are remembered better than uncertain ones. Should the coach ask students to articulate *why* they chose a wrong answer before explaining the correction? When does this help, and when does it frustrate?

**4. Spaced repetition**
Q-Primer randomizes question order but does not schedule review based on forgetting curves. For exam prep specifically — is spaced repetition essential for the tool to be pedagogically serious, or is a "drill wrong answers" mode sufficient?

**5. Teacher control over the coach**
Teachers can include annotations in question banks that guide the AI's explanations. Is free-text annotation sufficient, or should there be structured ways to constrain the coach — for example, specifying which analogies or frameworks to use or avoid for a given course level?

**6. Where AI explanation breaks down**
What types of questions or concepts are poorly served by text-based AI explanation? Should the tool flag these and direct students to other resources — videos, worked examples, lab time? What does your discipline-specific experience suggest about what students genuinely cannot learn from a text coaching conversation?

---

## How to Give Feedback

**GitHub Issues are the preferred channel.** Open an issue with your thoughts, questions, or concerns — tag it `pedagogy` if you'd like to flag it for the teaching/learning design discussion specifically.

If you'd prefer to share feedback privately, reach out at **q-primer@highcentrality.com**.

All feedback is welcome — early input shapes the design most effectively, but there is no cutoff. Issues tagged `pedagogy` are tracked separately from technical work.

---

## Project Documentation

| Document | Audience | Contents |
|----------|----------|----------|
| [`docs/00-introduction.md`](docs/00-introduction.md) | Anyone | What Q-Primer is and what it feels like to use |
| [`docs/01-question-bank-schema.md`](docs/01-question-bank-schema.md) | Bank contributors | JSON format for question banks |
| [`docs/02-app-architecture.md`](docs/02-app-architecture.md) | Developers | Component breakdown and state design |
| [`docs/03-prompt-design.md`](docs/03-prompt-design.md) | Developers + curious educators | How the AI coach is prompted |
| [`docs/04-claude-code-brief.md`](docs/04-claude-code-brief.md) | Developers | Implementation specification |
| [`docs/05-deferred-features.md`](docs/05-deferred-features.md) | Anyone | What's planned but not in v1 |
| [`docs/06-use-cases-and-user-stories.md`](docs/06-use-cases-and-user-stories.md) | **Educators** | User personas, use cases, and open pedagogical questions |

---

## License

MIT License — see [`LICENSE`](LICENSE) (to be added).

---

*Q-Primer is an open-source project. Contributions of question banks, code, and pedagogical expertise are all welcome.*
