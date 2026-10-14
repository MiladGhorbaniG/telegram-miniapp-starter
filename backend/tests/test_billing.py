import pytest

from booknook_core.billing import apply_provider_event, start_checkout


def test_checkout_ids_are_stable() -> None:
    started = start_checkout(7, "reading-room")
    assert started["status"] == "pending"
    assert started["checkout_id"] == "chk_7_reading-room"
    assert started["amount_cents"] == 900
    again = start_checkout(7, "reading-room", nonce="ab12")
    assert again["checkout_id"] == "chk_7_reading-room_ab12"


def test_unknown_plan() -> None:
    with pytest.raises(ValueError):
        start_checkout(7, "penthouse")


def test_completion_activates_once() -> None:
    started = start_checkout(7, "reading-room")
    active = apply_provider_event(
        started,
        {"type": "checkout.completed", "checkout_id": started["checkout_id"]},
    )
    assert active["status"] == "active"
    again = apply_provider_event(
        active,
        {"type": "checkout.completed", "checkout_id": started["checkout_id"]},
    )
    assert again["status"] == "active"


def test_rejects_other_events_and_mismatched_ids() -> None:
    started = start_checkout(7, "reading-room")
    with pytest.raises(ValueError, match="unsupported"):
        apply_provider_event(started, {"type": "refunded", "checkout_id": started["checkout_id"]})
    with pytest.raises(ValueError, match="mismatch"):
        apply_provider_event(started, {"type": "checkout.completed", "checkout_id": "other"})
