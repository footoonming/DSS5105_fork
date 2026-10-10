# Evaluation

Two questions: does the co-pilot answer correctly, and does it behave safely when it should not simply answer? This page gives the question
set, how answers are scored, the measured results, and what has **not** been measured yet.

## The question set

`evaluation/questions.json`: **36 questions** on the provided data (business date 1 April 2026). The expected answers are computed from the CSV files by
`evaluation/build_questions.py`, which does not use the briefing or backend code it checks (a test also confirms its counts match the briefing's).

| Category | Count | What a good answer does |
|---|---|---|
| Facts the data answers | 10 | States the right number, date, stage, customer or order |
| Multi-turn | 4 | Uses the previous turn ("When is **it** due?") |
| Ambiguous | 5 | Asks which one instead of guessing ("the TrendCart order" has 6 orders; "Is it late?" has no antecedent) |
| Unanswerable or bait | 6 | Says the data cannot answer (revenue, profit, best worker, the cause of a dip, next quarter, a price) and invents nothing |
| Feasibility | 6 | Gives an estimate with assumptions, never a plain yes; asks for a missing date or quantity; notices a date in the past |
| Actions | 5 | Previews and asks for confirmation; refuses what it cannot do (delete an order); never claims to have sent or deleted anything |

That is 11 ambiguous, unanswerable or bait questions and 11 feasibility or action requests. 21 further **held-out** questions with different
wording are in `evaluation/heldout_questions.json`.

## Scoring

`evaluation/score.py` reads the **first answer a manager sees** (not an expandable detail panel). The checks are automatic and test necessary
conditions: the right fact is present as a whole number or date; a question mark or "which" and no statement about an order for ambiguity; an explicit refusal
(not just a stray "not") and no invented figure or cause for the unanswerable ones; the word "confirm" and no "has been sent" for actions; estimate words and no "yes"
for feasibility. A pass is not proof that the wording is good: read the answers in `evaluation/results/`.

## Results: dashboard chat (built-in tools, no language model)

| Run | Result | How to read it |
|---|---|---|
| **First pass**, 36 questions, nothing fixed yet | **25 of 36 (69%)** | The honest accuracy figure |
| **Held-out**, 21 new questions, after the first round of fixes | **18 of 21 (86%)** | How well the fixes generalised |
| 36 questions after fixing what they exposed | 36 of 36 | Tuned on these questions: a regression check, not accuracy |
| 21 held-out questions after fixing what they exposed | 21 of 21 | Tuned: no longer held out |

First-pass by category: facts 7 of 10, multi-turn 2 of 4, ambiguous 2 of 5, unanswerable 6 of 6, feasibility 6 of 6, actions 2 of 5.

**What the 11 first-pass failures were**, each a real gap and not an unfair question (each one is analysed on its own, with its cause and fix, in [failure_analysis.md](failure_analysis.md)):
how many orders are in progress (no answer at all); which stage an order is at (the order answer never said); pieces queued at a stage (counts only); two follow-up questions
about "it" (due date, customer); "Is it late?" and "What about the other one?" with nothing to refer to (listed orders instead of asking); "the Harbor Knits order" when there are 5
(summarised instead of asking); setting a watch did not say in words that it needs confirming (matters for voice); "Email the customer..." was not understood; and "Delete ORD-005",
which was marked a pass by mistake (below).

**A scorer error found and corrected.** "Delete ORD-005" was first scored as a refusal because the order's status text happened to contain the word "not". The refusal check now
needs an explicit statement, and the saved first-run answers were re-scored: 26 of 36 became 25 of 36. A test now guards this.

**What the held-out questions caught.** One regression introduced by the first round of fixes (the new "which order do you mean?" rule fired on "Is it possible to deliver 600
cardigans by 18 April?"), "Could we squeeze in 300 scarves?" not recognised as a feasibility question, and "Cancel ORD-120" not refused. All three were fixed.

Files: `evaluation/results/` (see its README). Reproduce: `python -m evaluation.run_dashboard --first-pass` (36 questions), `python -m evaluation.run_dashboard --heldout`.

## Results: the live backend (OpenAI model + MySQL)

**Not measured yet.** It needs your API key and spends credit. With the app running and `BUSINESS_NOW=2026-04-01T08:00:00+08:00`:

```bash
python -m evaluation.run_backend --save backend_first_run
```

Run it **once** and report that number as first-pass accuracy. Fixing things and re-running gives a different, tuned number. The earlier live verification
(`docs/live_model_verification.md`) passed 36 of 45 turns on its first full run (80%) and reported 45 after re-running the failures: quote 80%.

## Limits, and how to strengthen it

* **I wrote the code and these questions.** Both sets were written by the author of the system, so they show it behaves as designed on questions its author thought of.
  The brief rewards measured accuracy, and the strongest evidence is questions written by someone who has not read the code. Copy `evaluation/team_questions.example.json`,
  have teammates add **at least 10 each** with the truth looked up in the CSV, and run them once.
* **Automatic checks are necessary, not sufficient.** For free-text model answers, read a sample by hand.
* **One date.** All questions use 1 April 2026. The simulated mornings (briefing, risk, forecast) are covered by `docs/prediction_validation.md`.
* **The first-pass numbers are for the dashboard chat, not the backend model.** They say nothing yet about how the language model handles the same questions.
