# Sprint 1 presentation (5 minutes)

[`ThreadPilot_Sprint1_5min.pptx`](ThreadPilot_Sprint1_5min.pptx): 6 slides, about 4 minutes 40 seconds when spoken, with a timed script in each
slide's speaker notes. Edit it in PowerPoint; every slide is native text, shapes and one native chart.

Rule used to write it: **a number goes on a slide only if a file in this repository states it.** Anything the team does not have yet is a
yellow **ADD:** tag on the slide, never a guess.

## Where every number on the slides comes from

| Slide | Claim | Source |
|---|---|---|
| 1 | Three-line summary of the simulated morning of 9 April 2026 (2,567 pieces, Washing below normal, 6 TrendCart orders stopped, 6 overdue, 9 due) | [`briefings/2026-04-09.json`](../../briefings/2026-04-09.json), `headline` |
| 2 | The five questions at 7:00, 9:40, 11:15, 14:30, 17:00 | Track 1 brief; replies follow [README.md](../../../README.md), "What it does" |
| 2 | "TrendCart has six orders" | [evaluation.md](../evaluation.md), ambiguous questions; the 9 April briefing finding |
| 3 | 33 tools in one table | [tool_spec.md](../tool_spec.md) (B1 to B15, D1 to D18) |
| 3 | "Normal" = previous 8 same weekdays, band = mean ± larger of 1.5 SD or 5% of the mean, Sundays closed | [tool_spec.md](../tool_spec.md), "Definitions the tools share" |
| 3 | 15-minute confirmation key, every executed action logged | [tool_spec.md](../tool_spec.md), B11 and "How actions stay safe" |
| 3 | The model never does the arithmetic | [README.md](../../../README.md), rule 1 |
| 4 | Screenshot (dashboard + chat, 9 April 2026, simulated day 8) and the ORD-008 expedite answer (saves 7 working days, adds 3 elsewhere) | [`../images/chat.png`](../images/chat.png) |
| 5 | First pass 25 of 36 (69%), held-out 18 of 21 (86%), first-pass by category | [evaluation.md](../evaluation.md), "Results: dashboard chat" |
| 5 | Discovery found 5 of 5 planted events, 1 to 5 days after each started | [README.md](../../../README.md), "Briefing, simulator and predictions" |
| 5 | Feasibility ranges contained the real finish in 14 of 14 cases | [prediction_validation.md](../prediction_validation.md), section 3 |
| 5 | Live backend accuracy: **not measured yet** | [evaluation.md](../evaluation.md), "Results: the live backend" |
| 6 | Forecast no better than repeating the last period | [prediction_validation.md](../prediction_validation.md), section 3 |
| 6 | About 29 working days of work in progress against 12 to 30 allowed | [prediction_validation.md](../prediction_validation.md), section 1 |
| 6 | Next steps | [evaluation.md](../evaluation.md), "Limits"; [README.md](../../../README.md), "Limitations" |
| 6 | Sprint 1 Fri 16 Oct, Sprint 2 Fri 30 Oct, Sprint 3 Fri 13 Nov, final zip Sun 15 Nov 2026 | Course schedule as the team recorded it; check against the official timetable |

The first-pass and held-out figures are for the **dashboard chat** (built-in tools, no language model). The discovery and feasibility figures
come from the team's own simulator, so they show internal consistency, not real-world accuracy. The slides say both.

## Before presenting (things only the team can supply)

- [ ] Title slide: **group number** and the **sixth team member's name**.
- [ ] Slide 6: **what Sprint 2 and Sprint 3 will deliver, and who owns each part** (the yellow tag).
- [ ] Run the live-backend evaluation **once** and replace the "Not measured yet" bar on slide 5 with that number, reported as first pass
      ([how](../evaluation.md#results-the-live-backend-openai-model--mysql)). Do not re-run and report the better number.
- [ ] Each teammate adds at least 10 evaluation questions of their own, with the answer looked up in the CSV
      ([`evaluation/team_questions.example.json`](../../evaluation/team_questions.example.json)). Then the question set is not only
      written by the author of the code.
- [ ] Decide whether to show per-person contributions. Nothing in the repository records them, so the deck has none.
- [ ] Not in the repository, so not on the slides: any feedback from a real general manager, and any measured time saved.

## Demo on the day

Slide 4's speaker notes list the prompts in order. They run on the briefing demo ([`demo/briefing_demo.html`](../../demo/briefing_demo.html),
no installation, no key) on 9 April. In the app it is **Morning Briefing** in the left menu once this branch is merged and the site is
redeployed. Say plainly that the demo chat uses built-in tools, not a language model.
