# Use Cases & User Stories
## Q-Primer — v1.0
### For Teacher Review & Feedback

---

## Purpose of This Document

This document describes who uses Q-Primer, why, and what they need from it. It is written for educators and subject matter experts to review and critique. We are particularly interested in what we have missed, misunderstood, or underweighted from a pedagogical standpoint.

Questions we'd love feedback on are marked **[TEACHER FEEDBACK REQUESTED]**.

---

## Personas

### P1 — The Self-Directed Adult Learner
*"I need to pass this exam and I learn by understanding, not memorizing."*

Maya is 34, works in IT infrastructure, and is studying for the Ham Radio General Class license. She has a technical background but no formal RF training. She studies in 30-minute sessions after work, usually on a laptop. She finds flashcard-style drilling demotivating — she wants to know *why*, not just *what*. She is comfortable with technology but not a developer.

### P2 — The Returning Student
*"I know this material. The exam is what's tripping me up."*

David is 52, retired military, applying to a graduate program in public policy after two decades in logistics and operations. He is studying for the GRE, which he last took in his late twenties. His quantitative reasoning is solid from years of operational planning, but his verbal score on practice tests is inconsistent — he understands the concepts but gets tripped up by the specific question logic and vocabulary the GRE uses as a filter. He wants targeted practice on problem areas without being forced through content he already knows cold. He studies in focused 45-minute blocks, early morning, before the rest of the house wakes up.

### P3 — The Classroom Teacher
*"I want my students to have a tool that reinforces what I taught, not one that teaches differently."*

Ms. Chen teaches AP Chemistry at a public high school. She writes her own practice question banks aligned to her curriculum. She is not a developer but is comfortable with structured file formats if they are well-documented. She wants to give students a self-study tool they can use outside class, and she wants the AI coach's explanations to align with how she teaches the material — not introduce alternate frameworks that confuse students before the exam.

### P4 — The Subject Matter Expert / Bank Contributor
*"I want to publish a question bank for my community."*

James is a Volunteer Examiner for the ARRL and has been administering ham radio exams for 15 years. He wants to contribute a Technician Class question bank to the repo so other VEs and clubs can point students to it. He is not technical but can follow a documented format spec with examples.

### P5 — The Casual / Low-Stakes Learner
*"I'm just curious. I'm not sure I'm even going to take the exam."*

Sofia is exploring amateur radio as a hobby. She hasn't committed to taking the exam. She wants to poke around the material, understand the concepts, and see if it interests her enough to pursue. She has no technical background and is easily put off by jargon.

---

## Use Cases

Use cases describe interactions at the system level — what the system does, not who does it.

---

### UC-01: Load a Question Bank

**Actor:** Any user
**Precondition:** User has opened the app
**Trigger:** User selects a question bank file or (future) chooses from a published bank list

**Main Flow:**
1. User uploads a JSON question bank file
2. System validates the file against the schema
3. System displays bank title, question count, and subelement/group structure
4. System confirms bank is ready to use

**Alternate Flow — Validation Failure:**
1. File fails validation
2. System displays specific error identifying which field or rule failed
3. User can upload a different file or correct the current one

**Postcondition:** Bank is loaded in memory, app is ready to begin a session

---

### UC-02: Configure Study Session

**Actor:** Any user
**Precondition:** Bank is loaded
**Trigger:** User proceeds to session setup

**Main Flow:**
1. User enters (or reviews existing) student profile — background, experience, goals
2. User enters API key
3. User optionally selects a filter (subelement, group, or full pool) — *filter UI deferred to post-v1, full pool only in v1*
4. User starts session

**Postcondition:** Session initialized, quiz begins

---

### UC-03: Answer a Question

**Actor:** Any user
**Precondition:** Active session, question displayed
**Trigger:** Question is presented

**Main Flow:**
1. System displays question text and four answer choices verbatim from bank
2. User selects an answer
3. User submits
4. System reveals correct answer with visual feedback (correct/incorrect)
5. System automatically sends question context to AI coach
6. Coach explanation appears in coach panel

**Alternate Flow — Skip:**
1. User clicks Skip
2. Question recorded as skipped (not wrong)
3. Next question presented
4. Coach panel is not triggered for skipped questions

**Postcondition:** Answer recorded in session state, score updated, coach explanation displayed

---

### UC-04: Engage with AI Coach Explanation

**Actor:** Any user
**Precondition:** Question answered, coach explanation displayed
**Trigger:** Coach explanation appears automatically

**Main Flow:**
1. Coach explains why the correct answer is correct
2. Coach explains why each wrong answer is wrong
3. User reads explanation

**Alternate Flow — Follow-up Question:**
1. User types a follow-up question in the coach panel input
2. Coach responds in context of the current question
3. User may ask multiple follow-ups before moving on

**Alternate Flow — Pre-answer Explanation:**
1. Before answering, user requests explanation of the concept
2. Coach explains the underlying concept without revealing the correct answer
3. User then answers the question

**Postcondition:** User moves to next question when ready

---

### UC-05: Complete a Study Session

**Actor:** Any user
**Precondition:** Active session
**Trigger:** All questions answered/skipped, or user ends session manually

**Main Flow:**
1. System detects all questions in scope have been answered or skipped
2. System displays session summary: score, questions correct/wrong/skipped, time elapsed
3. User returns to setup screen

**Alternate Flow — Manual End:**
1. User clicks "End Session"
2. System displays same summary
3. Session data preserved in localStorage

**Postcondition:** Session complete, state persisted

---

### UC-06: Contribute a Question Bank

**Actor:** Subject Matter Expert (P4)
**Precondition:** Source material (existing question pool, textbook questions, teacher-written questions) available
**Trigger:** Contributor wants to publish a bank

**Main Flow:**
1. Contributor reads bank format spec and example
2. Contributor converts source material to JSON format (manually or with ETL tools when available)
3. Contributor validates JSON against schema
4. Contributor submits bank to repo via pull request
5. Bank becomes available to all users

**Postcondition:** Bank published, accessible to community

---

## User Stories

User stories describe what a specific persona needs and why. Format: *As a [persona], I want [capability] so that [outcome].*

---

### Self-Directed Adult Learner (P1 — Maya)

**US-101**
As a self-directed learner, I want the AI coach to calibrate its explanations to my technical background so that I don't waste time on concepts I already understand.

**US-102**
As a self-directed learner, I want to ask follow-up questions about a concept before moving on so that I can fill specific gaps in my understanding rather than just accepting an answer.

**US-103**
As a self-directed learner, I want to see my running score during a session so that I can gauge my readiness and adjust my study focus.

**US-104**
As a self-directed learner, I want the question text and answer choices to be exactly as they will appear on the actual exam so that I am practicing the real thing, not a paraphrase.

**US-105**
As a self-directed learner, I want my profile and preferences to persist between sessions so that I don't have to reconfigure the tool every time I sit down to study.

**[TEACHER FEEDBACK REQUESTED]**
*US-104 reflects a deliberate design choice: we never paraphrase question text. Is this always pedagogically sound? Are there cases where a teacher would want the coach to reframe or simplify a question to aid comprehension before presenting the canonical version?*

---

### Returning Student (P2 — David)

**US-201**
As a returning student who knows my weak areas, I want to filter practice to specific topic areas so that I spend my limited morning study time where it matters most — GRE verbal reasoning, not quantitative, which I have under control.
*(Filter UI deferred to post-v1 — architecture supports it)*

**US-202**
As a returning student, I want the coach to recognize when I've gotten a question wrong multiple times and try a different explanatory approach so that I'm not re-reading the same explanation that didn't work the first time.

**US-203**
As a returning student, I want to see which specific questions I've gotten wrong so that I can identify patterns — am I missing a specific question type, or a vocabulary cluster, or a reasoning pattern the GRE uses repeatedly?

**US-204**
As a returning student, I want to skip questions I already know cold without it counting against my score so that my results reflect actual weak areas, not a general average across everything.

**US-205**
As a returning student who is older than the typical test-taker, I want the coach to give me direct, substantive explanations — not reassuring or simplified ones — so that I can close specific gaps efficiently without feeling patronized.

**[TEACHER FEEDBACK REQUESTED]**
*US-202 implies the coach should vary its explanatory strategy on repeated wrong answers. What pedagogical strategies are most effective for adult returning learners specifically — analogy, worked example, Socratic questioning, breaking the concept into smaller pieces? Should the coach be prompted to explicitly try a different modality on a second or third wrong answer?*

**[MATH/SCIENCE TUTOR FEEDBACK]**
*US-203 and US-205 reflect assumptions about how adult learners with strong domain expertise but rusty test-taking skills engage with practice tools. Does this match your experience tutoring adults preparing for high-stakes exams? What does this type of learner most commonly get wrong about their own preparation?*

---

### Classroom Teacher (P3 — Ms. Chen)

**US-301**
As a teacher, I want to create a question bank from my own exam questions so that students use a tool aligned to my curriculum, not a generic one.

**US-302**
As a teacher, I want to include annotations in my question bank that guide the AI coach's explanations so that the coach reinforces my teaching approach rather than introducing conflicting frameworks.

**US-303**
As a teacher, I want to pre-populate a student profile describing my course level and prerequisites so that students don't have to configure the tool themselves.

**US-304**
As a teacher, I want the tool to be usable without installation or accounts so that I can recommend it to students without a tech support burden.

**US-305**
As a teacher, I want to understand what the AI coach will and won't do so that I can confidently recommend the tool without worrying it will teach incorrect content.

**[TEACHER FEEDBACK REQUESTED]**
*US-302 raises a significant question: how much control should a teacher have over the coach's explanatory style and content? The annotation field currently passes free-text context to the coach. Should there be a more structured way to constrain or guide explanations — for example, specifying which analogies to use or avoid, or which frameworks are in scope for this course level?*

*US-303 is currently partially supported (student profile persists in localStorage) but there is no teacher-to-student profile distribution mechanism in v1. Is this a significant gap for classroom use?*

---

### Subject Matter Expert / Bank Contributor (P4 — James)

**US-401**
As a bank contributor, I want a clearly documented format spec with a worked example so that I can create a valid bank without developer help.

**US-402**
As a bank contributor, I want a validation tool that tells me specifically what's wrong with my file so that I can fix errors without guessing.

**US-403**
As a bank contributor, I want to include annotations for questions that reference figures or diagrams so that the AI coach can explain visual content that doesn't exist in text form.

**US-404**
As a bank contributor, I want my bank to be versioned so that corrections and updates don't silently replace the version students were studying from.

**[TEACHER FEEDBACK REQUESTED]**
*US-403 asks contributors to describe visual content in text for the AI to reason about. Is this a reasonable burden to place on contributors? Are there common question types (circuit diagrams, anatomical figures, geometric proofs, musical notation) where this approach breaks down?*

---

### Casual Learner (P5 — Sofia)

**US-501**
As a casual learner with no technical background, I want the coach to explain concepts in plain language without assuming prior knowledge so that I can explore the material without feeling lost.

**US-502**
As a casual learner, I want to explore questions by topic rather than being forced through the full pool in order so that I can follow my curiosity.

**US-503**
As a casual learner, I want the setup process to be short and clear so that I don't give up before I start.

**US-504**
As a casual learner, I want to understand what the Anthropic API key is and why I need it, with clear instructions, so that the setup doesn't feel like a technical barrier.

**[TEACHER FEEDBACK REQUESTED]**
*US-504 is a real onboarding friction point. The API key requirement is necessary but non-obvious to non-technical users. We plan to document setup clearly in the README. Are there other friction points in this flow that teachers would anticipate their students encountering?*

---

## Open Pedagogical Questions for Reviewer Discussion

Beyond the specific feedback requests above, we would value educator perspective on the following. Reviewer-specific callouts indicate where a particular reviewer's expertise is most directly relevant — but all reviewers should feel free to respond to any question.

---

**1. Immediate answer reveal vs. delayed feedback**
Q-Primer reveals the correct answer immediately after the student submits. Some learning research suggests delayed feedback — answering several questions before seeing results — produces better long-term retention. Should this be configurable? Is the answer different for exam prep vs. conceptual learning?

`[AP TECH TEACHER FEEDBACK]` — Does your classroom experience support immediate or delayed feedback for this age group and subject matter?
`[MATH/SCIENCE TUTOR FEEDBACK]` — Does your tutoring experience suggest a difference between adult learners and younger students on this question?

---

**2. Explanation before vs. after answering**
The current design presents questions cold — no scaffolding before the student commits to an answer. A "explain before answering" path exists but is on-demand only, not the default. Is this the right default for exam preparation specifically? Is there a case for making pre-answer scaffolding the default for certain question types?

`[AP TECH TEACHER FEEDBACK]` — For middle-school students encountering unfamiliar vocabulary in a question stem, is cold presentation appropriate or does it create avoidable frustration?
`[MATH/SCIENCE TUTOR FEEDBACK]` — For conceptually dense questions (e.g., GRE analytical reasoning, advanced math), does cold presentation serve the learner or does it entrench wrong intuitions before the correction arrives?

---

**3. The role of wrong answers in learning**
Research on the "hypercorrection effect" suggests that confidently wrong answers, once corrected, are remembered better than uncertain ones. Should the coach treat confidently-wrong answers differently — e.g., by asking the student to articulate why they chose that answer before explaining the correction?

`[MATH/SCIENCE TUTOR FEEDBACK]` — This is particularly relevant for quantitative questions where a wrong answer often reflects a specific misconception. Does asking "why did you choose that?" before correcting improve retention in your experience?
`[VE FEEDBACK]` — Ham exam candidates often have strong but wrong intuitions about RF behavior. Does this pattern match what you see at exam sessions?

---

**4. Spaced repetition**
Q-Primer currently has no spaced repetition mechanism — questions are randomized but not scheduled based on forgetting curves. For exam prep specifically, how important is this? Is "drill wrong answers" sufficient, or is a proper spaced repetition scheduler needed for the tool to be pedagogically serious?

`[MATH/SCIENCE TUTOR FEEDBACK]` — You likely have direct experience with students who crammed vs. distributed their practice. What's your read on whether SRS is essential or nice-to-have for this use case?
`[AP TECH TEACHER FEEDBACK]` — Do your students have the self-discipline to use a spaced repetition system, or does the scheduling itself become a barrier?

---

**5. Metacognitive scaffolding**
Should the coach ever ask the student to predict their confidence before answering ("how sure are you about this one?")? Confidence calibration is a distinct skill from content knowledge, and miscalibration — particularly overconfidence — is a documented exam failure mode.

`[MATH/SCIENCE TUTOR FEEDBACK]` — Confidence calibration seems especially relevant for adult learners with domain expertise who assume their background knowledge transfers cleanly to exam format. Does this match your experience with GRE or similar candidates?
`[AP TECH TEACHER FEEDBACK]` — Is confidence calibration a meaningful concept for middle-school students, or is it developmentally premature to make it explicit?

---

**6. The limits of AI explanation**
Where does AI coaching break down as a pedagogical tool? What types of questions or concepts are poorly served by text-based AI explanation — and should the tool flag these questions and suggest the student seek alternative resources (videos, worked examples, lab time)?

`[ALL REVIEWERS]` — This is the question we are least equipped to answer ourselves. Your discipline-specific experience with what students actually struggle to learn from text alone is the most valuable input we can receive.

`[VE FEEDBACK]` — Are there ham exam topics where you consistently see candidates fail despite understanding the text-based explanation — topics that only click with hands-on or visual experience?
`[MATH/SCIENCE TUTOR FEEDBACK]` — Are there question types in the GRE or math curriculum where AI explanation is structurally inadequate — not just weak, but the wrong tool entirely?
`[AP TECH TEACHER FEEDBACK]` — For your magnet school students, are there CS concepts that require interactive or visual tools that a text coaching conversation simply cannot substitute for?

---

*Document version 1.0 — for SME review*
*Part of Q-Primer specification set: see also 01-question-bank-schema.md, 02-app-architecture.md, 03-prompt-design.md, 04-claude-code-brief.md*
