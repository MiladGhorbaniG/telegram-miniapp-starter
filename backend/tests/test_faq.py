from booknook_bot.handlers import handle_text
from booknook_core.faq import MockFaqModel, answer_faq, rank_entries

ENTRIES = [
    {
        "id": "hours",
        "question": "When is the reading room open?",
        "answer": "Tuesday through Sunday.",
    },
    {
        "id": "late-fee",
        "question": "What is the late fee?",
        "answer": "One book credit per day after seven days.",
    },
]


def test_rank_prefers_the_late_fee_note() -> None:
    ranked = rank_entries("late fee after seven days", ENTRIES)
    assert ranked[0]["id"] == "late-fee"


def test_empty_question_has_no_source() -> None:
    result = answer_faq("???", ENTRIES, MockFaqModel())
    assert result["sources"] == []
    assert "could not find" in result["answer"]


def test_bot_commands() -> None:
    assert handle_text("/start", ENTRIES).startswith("BookNook desk")
    assert handle_text("/faq", ENTRIES).startswith("Add a question")
    assert "seven days" in handle_text("/faq what is the late fee?", ENTRIES)
    assert handle_text("/help", ENTRIES).startswith("Try /start")
