# Saved results

| File | What it is | Counts as |
|---|---|---|
| `dashboard_chat_first_run.json` | The 36 main questions, run once on the dashboard chat before any fix | **First-pass accuracy** |
| `dashboard_chat_heldout.json` | 21 new, differently worded questions, run once after the first round of fixes and before the second | **Held-out accuracy** |
| `dashboard_chat_after_fixes.json` | The 36 main questions after the gaps they exposed were fixed | Tuned: a regression check, not an accuracy claim |
| `dashboard_chat_heldout_after_fixes.json` | The 21 held-out questions after the gaps they exposed were fixed | Tuned: no longer held out |

Re-score any file with the current scorer without asking the system again: `python -m evaluation.score --rescore evaluation/results/FILE.json`.
The backend (live model) has not been run yet: `python -m evaluation.run_backend --save backend_first_run`, once, and report that number.
