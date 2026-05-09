# Q-Primer — Introduction
## What It Is, How It Works, and What It Feels Like to Use It

---

Q-Primer is a free, open-source study tool that helps people prepare for multiple-choice examinations by combining straightforward quiz practice with an AI-powered coaching conversation. It runs entirely in a web browser — no software to install, no account to create, no app store. A student opens a single webpage, loads a set of practice questions, and starts studying. The tool is deliberately simple to set up because the learning, not the technology, is the point.

The practice questions come from a **question bank** — a structured file containing the complete pool of questions for a given exam, including all four answer choices and the correct answer for each. Question banks are plain text files in a documented format, which means teachers, subject matter experts, and community volunteers can create and share them. Q-Primer ships with a question bank for the FCC Amateur Radio General Class license exam, and others can be contributed by anyone following the format guide. When a student loads a question bank, they are loading the actual exam questions verbatim — the tool never paraphrases or rewrites them, because practicing with the exact wording of the real exam matters.

The AI coaching layer is what separates Q-Primer from a simple flashcard app. When a student answers a question, their answer, the correct answer, and the question itself are sent — privately and directly — to Anthropic's Claude AI via an **API**, which is a secure connection between the student's browser and Anthropic's servers. Claude then acts as a study coach: explaining why the correct answer is correct, why each wrong answer is wrong, and engaging in follow-up conversation if the student wants to go deeper. Critically, the AI never generates the questions themselves — it only explains them. The question bank is the authoritative source; the AI is the tutor. To use the AI coaching feature, students need an **API key** — a personal access credential from Anthropic that takes about five minutes to set up and costs only a small amount per study session, roughly the price of a few minutes of a human tutor's time. Clear setup instructions are included.

---

## A Happy Path: Aisha Studies for Her AP Computer Science Exam

Aisha is a seventh-grader in an accelerated program taking AP Computer Science Principles. Her teacher, Mr. Okafor, has created a Q-Primer question bank from his own practice exam questions and posted a link to it on the class website alongside a link to the Q-Primer app. He has also written a short student profile suggestion: *"You are studying for AP CSP. Assume the student understands basic programming concepts but may be less familiar with data representation, the internet protocol stack, and cybersecurity vocabulary."*

Aisha opens the Q-Primer link on her laptop after dinner. The setup screen asks her to do three things: load a question bank, enter her API key, and optionally describe her background. She downloads Mr. Okafor's question bank file and drags it into the app — the app confirms it loaded 75 questions across six topic areas. She pastes in her API key, which she set up earlier following the instructions in the README. In the profile box, she pastes Mr. Okafor's suggested text and adds one line of her own: *"I'm pretty comfortable with Python but networking concepts are confusing to me."* She clicks Start Studying.

The first question appears: a question about how data is represented in binary, with four answer choices labeled A through D. Aisha reads it, selects what she thinks is right, and clicks Submit. The app immediately highlights the correct answer in green — she got it right. In the panel to the right of the question, the AI coach's response appears within a few seconds: a short explanation of why her answer was correct, a note on why the other three choices were plausible but wrong, and a brief aside connecting binary representation to how image files are stored — something the coach inferred might resonate from her Python experience. Aisha hadn't thought about it that way before. She types a follow-up question: *"Wait, so is that why PNG files are so much smaller than BMPs?"* The coach responds directly, staying on topic, and explains lossless compression in two paragraphs that don't talk down to her.

She moves on. The next question is about internet protocols — her weak area. She gets it wrong. The coach explains the layered model carefully, using an analogy to mailing a letter that she finds clearer than the textbook's explanation. She makes a note. Over the next forty minutes she works through twenty-two questions, gets sixteen right, and has three extended coaching conversations on topics that genuinely confused her. At the bottom of the coach panel, a small counter shows she has used approximately 8,400 tokens this session — a number that means little to her now, but that she can check against her API usage dashboard if she ever wants to.

When she closes the browser, her profile and session score are saved locally on her laptop. The next time she opens Q-Primer, her profile is still there. Her wrong answers are recorded, and a future version of the tool will offer to drill her on them specifically. For now, she makes a note to ask Mr. Okafor about protocol layering in class tomorrow — which is, arguably, exactly what a good study tool should produce.

---

## What Q-Primer Does Not Do (Yet)

Q-Primer v1 is a focused tool. It does not track progress across multiple sessions in a way the coach can reference, does not generate summaries for teachers to review, and does not offer scheduling of review sessions based on what a student is likely to forget. These are planned features. The current version does one thing well: it puts a knowledgeable, patient, personalized explainer next to every practice question, available at any hour, for the cost of a few cents per session. For students who learn by understanding rather than memorizing, that turns out to be quite a lot.

---

*This document is part of the Q-Primer specification set. See also: 01-question-bank-schema.md, 02-app-architecture.md, 06-use-cases-and-user-stories.md*
