"""Keep the language model's own words out of what the manager reads.

The model's job in the live chat is to fill in a form (intent + slots); code runs the tools and writes the answer. Three
places could still let model-written content through, and this module closes them:

1. Numbers the model "extracted" from the message (quantities, observed output). A number the user never typed is
   dropped, so the server asks for it instead of computing with an invented value.
2. Free text the model "extracted" for a draft or a note. It must be the user's own words: every number in it must be
   in the user's messages, and most of its words too. Otherwise it is not used.
3. The finished answer. Every number in it must appear in the user's messages, a tool's result or the evidence rows
   (or be one of the code's own fixed constants). Anything else is reported as ungrounded: logged, returned in the
   response, and counted by the tests and the evaluation.
"""
import json
import re
from collections.abc import Iterable

NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w])")
WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "a": 1, "an": 1}
SCALE = {"hundred": 100, "thousand": 1000, "k": 1000}
STOP = {"the", "a", "an", "to", "of", "and", "or", "for", "on", "in", "at", "by", "is", "are", "be", "it", "this", "that",
        "with", "please", "we", "i", "you", "our", "their", "they", "them", "can", "will", "would", "should", "as", "from",
        "about", "add", "note", "say", "saying", "write", "draft", "message", "tell", "ask"}


def numbers(text: str) -> set[str]:
    """Every number in the text, in one normal form: no thousands separators, no trailing .0 ("1,200.0" -> "1200")."""
    out = set()
    for raw in NUMBER.findall(text or ""):
        value = raw.replace(",", "")
        if "." in value:
            value = value.rstrip("0").rstrip(".")
        out.add(value.lstrip("0") or "0")
    # "1.2k", "800k"
    for whole in re.findall(r"(\d+(?:\.\d+)?)\s*k\b", (text or "").lower()):
        out.add(str(round(float(whole) * 1000)))
    return out | spelled_numbers(text)


def spelled_numbers(text: str) -> set[str]:
    """Numbers written in words: "eight hundred", "two thousand", "one lost day"."""
    out, current, seen = set(), 0, False
    # Punctuation and digits end a number: "eight hundred, two" is 800 and 2, not 802.
    for word in re.findall(r"[a-z]+|[^a-z\s]", (text or "").lower()) + ["."]:
        if word in WORDS and word not in ("a", "an"):
            current += WORDS[word]
            seen = True
        elif word in SCALE and word != "k":
            current = (current or 1) * SCALE[word]
            seen = True
        elif word in ("a", "an"):
            continue
        else:
            if seen:
                out.add(str(current))
            current, seen = 0, False
    return out


def said(value: float | None, said_texts: Iterable[str]) -> bool:
    """Did the user type this number (in digits or words) in any of these messages?"""
    if value is None:
        return True
    found = set().union(*(numbers(t) for t in said_texts)) if said_texts else set()
    return str(int(value)) in found if float(value).is_integer() else str(value) in found


def own_words(text: str | None, said_texts: Iterable[str], share: float) -> bool:
    """Is this text made of the user's own words? Every number must be theirs, and at least `share` of its words."""
    if not text:
        return True
    said_texts = list(said_texts)
    if not numbers(text) <= set().union(*(numbers(t) for t in said_texts)):
        return False
    heard = set(re.findall(r"[a-z0-9]+", " ".join(said_texts).lower()))
    words = [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]
    return not words or sum(w in heard for w in words) / len(words) >= share


def flatten(*parts) -> str:
    return " ".join(p if isinstance(p, str) else json.dumps(p, default=str, ensure_ascii=False) for p in parts if p is not None)


def ungrounded(answer: str, sources: str, constants: Iterable[str] = ()) -> list[str]:
    """Numbers in the answer that appear in none of the sources and are not one of the code's own constants."""
    allowed = numbers(sources) | set(constants)
    return sorted(numbers(answer) - allowed, key=lambda n: (len(n), n))
