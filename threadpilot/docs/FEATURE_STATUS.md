# Feature status: the sprint list

Status key: **Done** (built and tested), **Built, with caveats** (works; read the caveat), **Stub** (the control exists, the effect needs the backend).

| # | Item | Status | Where, and what to know |
|---|---|---|---|
| **Prediction** | | | |
| 1 | Risk in the morning briefing, with a confidence or risk level | Built, with caveats | "At risk" card, risk shown in the order table, chat: "Which orders are high risk?". Model in `simulation/prediction.py`. Nearly all orders are late in this data, so levels spread little; the "working days late" figure ranks them. |
| 2 | Forecast order quantity, product type and customer | Built, with caveats | "Expected orders, next 2 weeks" card. Volume is no better than repeating the last period, and customers are no better than chance on the provided data; the card says so. |
| **AI co-pilot** | | | |
| 1 | Chat interface for free-form questions | Done | "Ask ThreadPilot". Built-in tools, not a language model; `?api=` connects a backend. Unusual phrasings fall back to a help message. |
| 2 | Voice input | Built, with caveats | Microphone button in the chat (browser speech recognition, so Chrome, Edge or Safari; needs microphone permission). Not tested in an automated way. |
| 3 | Alert triggers: what interrupts the manager and what waits for the briefing | Done | [alert_triggers.md](alert_triggers.md): every threshold, score formula and ranking rule. A test reads them back from the code, so the page cannot go stale. Thresholds are design choices for this data set, not tuned with a real manager. |
| 4 | What the co-pilot can do for you, and its limits | Done | [actions_and_limits.md](actions_and_limits.md): the preview, confirm, log rule, the worst case of each action, what it refuses and why, and what is not covered yet. |
| 5 | Conversation scenarios, including multi-turn | Done | [conversation_scenarios.md](conversation_scenarios.md): nine scenarios recorded from the real chat (vague question, follow-ups, unanswerable, feasibility, actions, watches). A test records them again, so the page shows what the chat does today. Recording them exposed six follow-ups that lost the thread; they are fixed and tested. |
| 6 | Boundaries between tools | Done | [tool_boundaries.md](tool_boundaries.md): the rules that draw each line, the retrieval decision and the failure we accepted, 27 questions recorded from the real chat with the tool that must and must not answer, and the places where our own tools disagree. A test re-records it. Probing found three chat defects (the manager's own number ignored, a stalled customer answered with an idle-order list, "show all orders" refused); all fixed and tested. |
| 7 | Live-path tools for the briefing and for refusing | Built, with caveats | `get_briefing` (reads the saved 07:00 briefing) and `explain_no_data` (says what the data does not hold) in `backend/app/`, tested with a stand-in classifier. **How often the live model picks these two intents is not measured.** |
| 8 | Discovery and one risk rule on the live path | Built, with caveats | `list_findings` on the live backend runs the briefing's own engine (eight kinds of finding, ranked by a stated score) on the database, and the saved 07:00 briefing carries the same findings. `assess_order_risk` now reports the dashboard's projected risk level. `backend/tests/test_discovery.py` holds both to the briefing page on four mornings, including a planted stalled customer. **How often the live model picks `discovery.findings` is not measured.** |
| **Interface and settings** | | | |
| 1 | Font size and typeface | Done | Settings: text size S, M, L, XL; typeface System, Inter, Serif, Monospace. Saved in the browser. |
| 2 | Target per stage, highlighted after 3 missed days | Done | Settings, then a strip above the output chart, a red pill in the summary, and chat: "Are any stages missing their target?". |
| 3 | Memo for an amended delivery date; table of amended specifications | Built, with caveats | "Memos" card. Notes in the browser only; the risk model does not apply them yet. SQL sketch in `docs/prediction_validation.md`. |
| 4 | View yesterday's or any previous day | Done | Date picker, arrow keys, Replay. |
| 5 | Split at-risk into overdue and approaching | Done | "At risk" card, two columns. |
| 6 | Hourly or daily refresh | Stub | Saved setting. Data is daily and the demo builds one briefing per morning; hourly needs a backend job. |
| 7 | Optimise for mobile | Done | Checked at phone width, including the largest text size (no sideways scrolling). |
| **Actionable** | | | |
| 1 | Right-hand follow-up panel; one-click email or Teams message | Built, with caveats | "Actions" on any at-risk order. "Open in email app" fills a mailto; "Copy Teams message" copies text; both are logged. No direct Teams posting. |
| 2 | Impact of expediting an overdue order; expedite now or later | Built, with caveats | Same panel, and chat: "Should we expedite ORD-120?". Net-lateness model; checked against the simulator (see `docs/prediction_validation.md`). |
| **Project files** | | | |
| 1 | Upload everything to the shared GitHub repository | Done | Update with the files in this change set. |
| **Presentation** | | | |
| 1 | "Brainstorm prompts to int..." (the line is cut off) | Draft below | If it meant prompts to *introduce* the co-pilot in the video, use the list below. |
| 2 | Sprint 1 slides (5 minutes) | Built, with caveats | [presentation/](presentation/): 8 slides in the order the course asks (problem and solution, architecture diagram, business value, progress, risk table, assumptions table, Sprint 2 roadmap with success criteria) plus 4 backup slides, real screenshots, timed speaker notes (about 4 minutes) and a source for every number. The file must be renamed `Presentation_GroupNN_Sprint1.pptx` with the group number. Group number, the sixth member and the owners are marked **ADD:** or **TEAM:**; the risk ratings and Sprint 2 success criteria are proposals the team has not agreed. |

## Draft: prompts for the 5-minute video

Run them in this order on **9 April** (the date picker, "Simulated day 8"):

1. "Did anything go wrong yesterday?" The three-line briefing, then "Show detail".
2. "Which orders are high risk?" Risk with confidence and how late.
3. "Should we expedite ORD-120?" The answer is "find the blocker first": it is part of the stalled TrendCart group, so moving it up the queue would not help.
4. "How is the TrendCart order doing?" It asks which of the six orders you mean.
5. "Can we take 800 hoodies by the 25th?" A range with stated assumptions, never a plain yes.
6. "What orders do we expect in the next two weeks?" A range, with the honest accuracy line.
7. "What's our revenue this month?" A refusal: no price data is held.
8. "Chase ORD-120", then confirm. Then open **Actions** on an order to show the email and Teams drafts.
9. "Tell me if ORD-120 hasn't moved by Friday", confirm, then step the date to Friday and watch it fire.

Be ready for these three questions:

* *"Why is almost everything late?"* The data describes it: about 29 working days of work in progress against 12 to 30 days allowed (`docs/prediction_validation.md`, section 1).
* *"Is the forecast accurate?"* On the provided data it is no better than repeating the last period; it is a rough range.
* *"Why does it so often say not to expedite?"* In a factory this behind, moving one order up mostly moves the delay onto others; the simulation confirms it.

## Required deliverables

| Deliverable | Status | Where |
|---|---|---|
| English README | Done | [README.md](../../README.md) |
| One-table tool specification (name, input, output, purpose, non-goals, failure mode) | Done: 37 entries (18 live, 19 dashboard); a test checks the live names against the code | [tool_spec.md](tool_spec.md) |
| Evaluation set of 30+ questions with 5+ ambiguous or unanswerable and 5+ feasibility or action | Done: 36 questions, plus 21 held out. **Backend (live model) accuracy not yet measured** | [evaluation.md](evaluation.md) |
| 10+ failure cases, each analysed individually | Done: the 12 first-pass failures, 3 found by probing and 6 from the bait questions | [failure_analysis.md](failure_analysis.md) |
| A page of honest reasoning about the boundaries between tools | Done | [tool_boundaries.md](tool_boundaries.md) |
| One inspectable definition of "normal" | Done, and checked by a test across backend, briefing and dashboard | [tool_spec.md](tool_spec.md), definitions |
| Reproducible set-up for lecturers | Done for Docker and the offline demo; CI runs the tests | [README.md](../../README.md) |
| 5-minute live presentation | Slides done in the course's order, with **ADD:** and **TEAM:** gaps; rename to the group number before uploading by 3:00 PM Fri 16 Oct (see the checklist in the folder) | [presentation/](presentation/) |
| 5-minute video | Not recorded yet; the prompts above are its script | |
