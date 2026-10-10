# Sprint 1 presentation (5 minutes)

[`ThreadPilot_Sprint1_5min.pptx`](ThreadPilot_Sprint1_5min.pptx): 7 slides and 1 backup, about 4 minutes 20 seconds when spoken, with a timed
script in each slide's speaker notes. Edit it in PowerPoint; the text, shapes and the chart are native, and the screenshots are real pictures of the
running demo ([`screens/`](screens/), made by [`scripts/capture_screenshots.py`](../../scripts/capture_screenshots.py), which types the
questions into the real chat box; nothing is mocked up).

Rule used to write it: **a number goes on a slide only if a file in this repository states it, or it is visible in a screenshot.** Anything the team does not have yet is a
yellow **ADD:** tag on the slide, never a guess.

## Where every number on the slides comes from

| Slide | Claim | Source |
|---|---|---|
| 1 | The morning page of Thursday 9 April 2026 (simulated day 8) | [`screens/01_briefing.png`](screens/01_briefing.png) |
| 2 | Three-line summary: 2,567 pieces, Washing below normal, all 6 TrendCart orders stopped, 6 overdue, 9 due this week | [`briefings/2026-04-09.json`](../../briefings/2026-04-09.json), `headline` and `kpis` |
| 2 | 34 orders in progress: 1 on track, 27 at risk, 6 late; generated 07:00 | [`briefings/2026-04-09.json`](../../briefings/2026-04-09.json), `status_counts`; the screenshot |
| 2 | Why it is a shared cause and not the queue | [alert_triggers.md](../alert_triggers.md), `customer_stalled` |
| 2 | Discovery found 5 of 5 planted events, 1 to 5 days after each started (speaker notes) | [README.md](../../../README.md), "Briefing, simulator and predictions" |
| 3 | Three chat screenshots: a vague question that asks which of six orders, three follow-ups about ORD-120, a refusal (revenue) and a partial answer (washing 297 against a usual 733) | [`screens/02`, `03`, `04`](screens/); the same turns are written out in [conversation_scenarios.md](../conversation_scenarios.md) (S2, S3, S4) |
| 3 | Recording the scenarios exposed six follow-ups that lost the thread; fixed and tested | [conversation_scenarios.md](../conversation_scenarios.md), "What recording these found"; `tests/test_chat.py` |
| 4 | 33 tools in one table | [tool_spec.md](../tool_spec.md) (B1 to B15, D1 to D18) |
| 4 | "Normal" = previous 8 same weekdays, band = mean ± larger of 1.5 SD or 5% of the mean, Sundays closed | [tool_spec.md](../tool_spec.md), "Definitions the tools share" |
| 4 | 15-minute confirmation key, every executed action logged | [tool_spec.md](../tool_spec.md), B11 and "How actions stay safe" |
| 4 | The model never does the arithmetic | [README.md](../../../README.md), rule 1 |
| 5 | Confirmation card with the worst case; chase logged, nothing sent; "Delete ORD-005" refused | [`screens/06`, `07`](screens/); [actions_and_limits.md](../actions_and_limits.md) |
| 5 | Key covers one order and one text, expires in 15 minutes, confirming twice does nothing | [tool_spec.md](../tool_spec.md), "How actions stay safe"; [actions_and_limits.md](../actions_and_limits.md) |
| 5 | One briefing at 07:00; otherwise only watches the manager sets and a stage that misses its target 3 days running | [alert_triggers.md](../alert_triggers.md), the table at the top |
| 6 | First pass 25 of 36 (69%), held-out 18 of 21 (86%), first-pass by category | [evaluation.md](../evaluation.md), "Results: dashboard chat" |
| 6 | Discovery found 5 of 5 planted events, 1 to 5 days after each started | [README.md](../../../README.md), "Briefing, simulator and predictions" |
| 6 | Feasibility ranges contained the real finish in 14 of 14 cases | [prediction_validation.md](../prediction_validation.md), section 3 |
| 6 | Live backend: 36 of 45 scripted turns passed on the first full batch (7 hit HTTP 429), all 45 only after re-running; **not yet run on the 36 questions** | [live_model_verification.md](../live_model_verification.md); [evaluation.md](../evaluation.md), "Results: the live backend" |
| 7 | Forecast no better than repeating the last period | [prediction_validation.md](../prediction_validation.md), section 3 |
| 7 | About 29 working days of work in progress against 12 to 30 allowed; 27 of 34 orders at risk, 6 late | [prediction_validation.md](../prediction_validation.md), section 1; the 9 April briefing |
| 7 | Next steps | [evaluation.md](../evaluation.md), "Limits"; [README.md](../../../README.md), "Limitations" |
| 7 | Sprint 1 Fri 16 Oct, Sprint 2 Fri 30 Oct, Sprint 3 Fri 13 Nov, final zip Sun 15 Nov 2026 | Course schedule as the team recorded it; check against the official timetable |
| 8 (backup) | Feasibility answer (800 hoodies by the 25th: finishes 1 to 8 May, bottleneck Packing) and a watch that fires on 10 April | [`screens/05`, `08`](screens/); [conversation_scenarios.md](../conversation_scenarios.md) (S5, S7) |

The first-pass and held-out figures are for the **dashboard chat** (built-in tools, no language model). The discovery and feasibility figures
come from the team's own simulator, so they show internal consistency, not real-world accuracy. The slides say both.

## Before presenting (things only the team can supply)

- [ ] Title slide: **group number** and the **sixth team member's name**.
- [ ] Slide 7: **what Sprint 2 and Sprint 3 will deliver, and who owns each part** (the yellow tag).
- [ ] Run the live-backend evaluation **once** and replace the "Not yet run on these 36 questions" line on slide 6 with that number, reported as first pass
      ([how](../evaluation.md#results-the-live-backend-openai-model--mysql)). Do not re-run and report the better number.
- [ ] Each teammate adds at least 10 evaluation questions of their own, with the answer looked up in the CSV
      ([`evaluation/team_questions.example.json`](../../evaluation/team_questions.example.json)). Then the question set is not only
      written by the author of the code.
- [ ] Decide whether to show per-person contributions. Nothing in the repository records them, so the deck has none.
- [ ] Not in the repository, so not on the slides: any feedback from a real general manager, and any measured time saved.

## Demo on the day

Slide 3's speaker notes say what to run; the full prompt order is in [FEATURE_STATUS.md](../FEATURE_STATUS.md). They run on the briefing demo ([`demo/briefing_demo.html`](../../demo/briefing_demo.html),
no installation, no key) on 9 April. In the app it is **Morning Briefing** in the left menu once this branch is merged and the site is
redeployed. Say plainly that the demo chat uses built-in tools, not a language model.
