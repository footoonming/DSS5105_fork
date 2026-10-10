"""Ask every evaluation question to the live backend (OpenAI model + MySQL) and score the answers.

    docker compose up -d        # the app must be running, seeded, with BUSINESS_NOW=2026-04-01T08:00:00+08:00 and your API key
    python -m evaluation.run_backend --first-pass --save backend_first_run     # --first-pass labels the figure; use it only for the very first run

Uses the chat endpoint, one fresh session per question (multi-turn questions share one session). It spends OpenAI credit
(about one model call per question). Run it ONCE and report that number: re-running after fixes is a different number.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from .score import load_questions, markdown, score, summary

URL = "http://127.0.0.1:8000/api/v1/workflow/chat"


def post(url: str, message: str, session_id: str | None) -> dict:
    body = json.dumps({"message": message, **({"session_id": session_id} if session_id else {})}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read())


def ask_all(questions: list[dict], url: str = URL) -> dict[str, str]:
    answers = {}
    for q in questions:
        session = None
        for turn in q["turns"]:
            reply = post(url, turn, session)
            session = (reply.get("state") or {}).get("session_id", session)
        answers[q["id"]] = reply.get("answer", "")
    return answers


def main() -> int:
    questions = load_questions()
    results = score(questions, ask_all(questions))
    print(markdown(results, "First-pass accuracy" if "--first-pass" in sys.argv else "Accuracy (not first-pass)"))
    for r in results:
        if not r["passed"]:
            print(f"\nFAIL {r['id']} [{r['category']}] {r['question']}\n     {r['answer'][:300]}")
    if "--save" in sys.argv:
        name = sys.argv[sys.argv.index("--save") + 1]
        (Path(__file__).parent / "results" / f"{name}.json").write_text(
            json.dumps({"system": "backend (OpenAI model + MySQL)", "summary": summary(results), "results": results}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
