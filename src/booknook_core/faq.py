from __future__ import annotations

import re
from typing import Protocol

TOKEN = re.compile(r"[a-z0-9]+")
STOP = {"a", "an", "the", "is", "are", "what", "where", "when", "do", "does", "of", "to", "in"}


class FaqModel(Protocol):
    def answer(self, question: str, entries: list[dict]) -> str:
        """Answer from the supplied desk notes only."""


class MockFaqModel:
    """Quotes the closest desk note. No network."""

    def answer(self, question: str, entries: list[dict]) -> str:
        del question
        if not entries:
            return "I could not find that in the BookNook desk notes."
        return str(entries[0]["answer"])


def tokens(text: str) -> set[str]:
    return {token for token in TOKEN.findall(text.lower()) if token not in STOP}


def rank_entries(question: str, entries: list[dict], limit: int = 3) -> list[dict]:
    wanted = tokens(question)
    scored: list[tuple[int, dict]] = []
    for entry in entries:
        overlap = len(wanted & tokens(f"{entry.get('question', '')} {entry.get('answer', '')}"))
        scored.append((overlap, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for score, entry in scored if score > 0][:limit]


def answer_faq(question: str, entries: list[dict], model: FaqModel) -> dict:
    top = rank_entries(question, entries)
    return {"answer": model.answer(question, top), "sources": [entry["id"] for entry in top]}
