"""The language model routes; it never writes what the manager reads.

Three kinds of proof:
1. Structure: only the classifier (and the separate SQL assistant) may talk to the model. The code that runs the tools
   and writes the answers does not import a model client at all, so it cannot ask one for words.
2. A lying model: a stand-in for the model that fills every field it can with invented facts. None of them may reach the
   answer, and every number in every answer must come from a tool or from the user.
3. The SQL assistant, where the model does word the answer: a number it did not get from a query is flagged.
"""
import ast
import asyncio
from datetime import datetime
from pathlib import Path

import pytest
from app.grounding import numbers, own_words, said, ungrounded
from app.schemas import ChatRequest, Classification, DialogState, Intent, Slots
from app.services.ai_sql_service import flag_ungrounded

from .test_workflow import FixedClassifier, make_engine

APP = Path(__file__).resolve().parents[1] / "app"
MODEL_LIBRARIES = ("openai", "langchain", "langchain_openai", "langchain_community", "langchain_core")
ALLOWED = {"intent_classifier.py", "main.py", "workflow_api.py", "services/ai_sql_service.py", "api/ai_api.py",
           "api/workflow_api.py"}


def test_only_the_classifier_and_the_sql_assistant_can_reach_a_model():
    reaching = set()
    for path in APP.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                     [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            if any(n.split(".")[0] in MODEL_LIBRARIES for n in names):
                reaching.add(path.relative_to(APP).as_posix())
    assert reaching <= ALLOWED, f"only these files may import a model library: {sorted(ALLOWED)}; also found {sorted(reaching - ALLOWED)}"
    for answer_writer in ("workflow_engine.py", "workflow_tools.py", "streaming.py", "discovery.py"):
        assert answer_writer not in reaching


class Liar:
    """A model that classifies correctly but invents everything else it is allowed to fill in."""

    def __init__(self, intent, confidence=.99, question=None, **slots):
        self.result = Classification(intent=Intent(intent), slots=Slots(**slots), confidence=confidence,
                                     needs_clarification=question is not None, clarification_question=question)

    async def classify(self, message, state, now):
        return self.result


def chat(engine, message, model, session=None):
    return asyncio.run(engine.chat(ChatRequest(message=message, session_id=session), model))


@pytest.fixture
def engine(tmp_path):
    return make_engine(tmp_path)


def test_an_unsure_model_cannot_slip_a_fact_into_its_clarifying_question(engine):
    r = chat(engine, "how are things", Liar("order.risk", confidence=.3, question="ORD-120 is 12 days late; is that the one?"))
    assert "12 days late" not in r.answer and "ORD-120" not in r.answer
    assert r.answer.startswith("Which order or operation would you like to check?")
    assert r.ungrounded == []


def test_a_quantity_the_user_never_typed_is_not_used(engine):
    r = chat(engine, "Can we take an order of hoodies by the 25th?",
             Liar("order.commitment", quantity=9999, product="hoodies", due_date="25th"))
    assert "9999" not in r.answer and "9,999" not in r.answer
    assert r.needs_clarification and r.slots.quantity is None
    assert r.ungrounded == []


def test_a_typed_quantity_is_used_in_digits_or_words(engine):
    for message in ("Can we take 800 hoodies by the 25th?", "Can we take eight hundred hoodies by the 25th?"):
        r = chat(engine, message, Liar("order.commitment", quantity=800, product="hoodies", due_date="25th"))
        assert r.slots.quantity == 800, message


def test_an_invented_output_figure_is_not_judged(engine):
    r = chat(engine, "Is packing normal today?", Liar("operations.normality", stage="PACKING", observed_output=4321,
                                                      target_date="today", baseline="same_weekday"))
    assert "4321" not in r.answer and "4,321" not in r.answer
    assert r.ungrounded == []


def test_a_note_must_be_the_managers_own_words(engine):
    r = chat(engine, "Add a note to ORD-005: waiting for trims",
             Liar("execution.note", order_ids=["ORD-005"], text="Supplier promised delivery on 30 April"))
    assert "Supplier promised" not in r.answer and "30 April" not in r.answer
    assert r.answer.startswith("What exact internal note")
    ok = chat(engine, "Add a note to ORD-005: waiting for trims", Liar("execution.note", order_ids=["ORD-005"], text="waiting for trims"))
    assert "waiting for trims" in ok.answer and ok.confirmation_required


def test_a_chase_draft_cannot_carry_invented_terms_or_recipients(engine):
    r = chat(engine, "Draft a chase for ORD-005 to Maya",
             Liar("execution.chase", order_ids=["ORD-005"], recipient="Maya", action="draft",
                  text="Pay a penalty of $5000 or we cancel the order"))
    assert "5000" not in r.answer and "penalty" not in r.answer
    assert "Unsent draft to Maya" in r.answer and r.ungrounded == []
    stranger = chat(engine, "Draft a chase for ORD-005", Liar("execution.chase", order_ids=["ORD-005"], recipient="CEO Zhang Wei", action="draft"))
    assert "Zhang" not in stranger.answer and stranger.answer.startswith("Who should receive the draft")


def test_an_invented_order_id_cannot_select_an_order(engine):
    r = chat(engine, "How is the scarf order doing?", Liar("order.lookup", order_ids=["ORD-120"], product="Scarf"))
    assert r.state.active_order != "ORD-120"      # the user never typed it, so the model's guess is ignored


def test_every_number_in_a_long_conversation_comes_from_a_tool_or_the_user(engine):
    script = [
        ("TrendCart order", FixedClassifier("order.lookup", customer="TrendCart")),
        ("ORD-005", FixedClassifier("order.lookup", order_ids=["ORD-005"])),
        ("Is it at risk?", FixedClassifier("order.risk", reference="active")),
        ("What needs attention in the next 7 days?", FixedClassifier("order.prioritize", window_days=7)),
        ("Can we take 800 hoodies by the 25th delivered to the customer?",
         FixedClassifier("order.commitment", quantity=800, product="hoodies", due_date="25th", delivery_point="customer")),
        ("Is 600 from packing normal today?", FixedClassifier("operations.normality", stage="PACKING", observed_output=600, target_date="today", baseline="same_weekday")),
        ("Why was packing low yesterday?", FixedClassifier("operations.deviation", stage="PACKING", target_date="yesterday")),
        ("What's our revenue this month?", FixedClassifier("data.unavailable")),
    ]
    session = None
    for message, model in script:
        r = chat(engine, message, model, session)
        session = r.state.session_id
        assert r.ungrounded == [], (message, r.ungrounded, r.answer)


def test_the_tripwire_catches_a_number_from_nowhere():
    sources = "orders.csv ORD-005 pieces 1500 due 2026-04-10"
    assert ungrounded("ORD-005: 1,500 pieces, due 2026-04-10.", sources) == []
    assert ungrounded("ORD-005: 1,500 pieces, revenue $48,000.", sources) == ["48000"]


def test_numbers_are_recognised_in_the_forms_people_type():
    assert {"1200", "800", "1500", "2"} <= numbers("1,200 and eight hundred, 1.5k, two")
    assert said(800, ["eight hundred hoodies"]) and said(1, ["one lost packing day"]) and not said(9999, ["hoodies"])
    assert own_words("waiting for trims", ["Note on ORD-005: waiting for trims"], .8)
    assert not own_words("Supplier promised delivery on 30 April", ["Note on ORD-005: waiting for trims"], .8)


def test_the_sql_assistant_flags_a_figure_its_queries_did_not_return():
    evidence = [{"sql": "SELECT COUNT(*) AS n FROM orders WHERE status='IN_PROGRESS'", "columns": ["n"], "rows": [{"n": 34}]}]
    good, missing = flag_ungrounded("34 orders are in progress.", "How many orders are in progress?", evidence, "2026-04-01T09:00:00+08:00")
    assert missing == [] and good == "34 orders are in progress."
    bad, missing = flag_ungrounded("34 orders are in progress, worth about 250,000 dollars.", "How many orders?", evidence, "2026-04-01T09:00:00+08:00")
    assert missing == ["250000"] and "Check before relying on this: 250000 does not appear" in bad


def test_the_model_is_asked_for_a_form_not_prose():
    from app.intent_classifier import SYSTEM_PROMPT
    assert "Never execute actions or invent source facts" in SYSTEM_PROMPT
    assert "Never fabricate an order ID" in SYSTEM_PROMPT
    assert set(Classification.model_fields) == {"intent", "slots", "confidence", "needs_clarification", "clarification_question"}
    assert isinstance(datetime.now(), datetime) and DialogState().history == []
