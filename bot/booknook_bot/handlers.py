from __future__ import annotations

import json
from pathlib import Path

from booknook_core.faq import MockFaqModel, answer_faq


def handle_text(text: str, entries: list[dict], model: MockFaqModel | None = None) -> str:
    model = model or MockFaqModel()
    raw = (text or "").strip()
    if not raw or raw.startswith("/start"):
        return (
            "BookNook desk. Ask with /faq, for example: /faq what is the late fee?"
        )
    if raw.startswith("/faq"):
        question = raw[4:].strip()
        if not question:
            return "Add a question after /faq."
        return answer_faq(question, entries, model)["answer"]
    if raw.startswith("/"):
        return "Try /start or /faq."
    return answer_faq(raw, entries, model)["answer"]


def load_entries(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))
