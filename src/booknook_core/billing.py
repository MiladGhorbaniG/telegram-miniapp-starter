from __future__ import annotations

PLANS = {
    "reading-room": {
        "id": "reading-room",
        "title": "Reading room",
        "amount_cents": 900,
        "currency": "USD",
        "interval": "month",
        "blurb": "Four loans at a time and one Sunday guest.",
    }
}


def start_checkout(user_id: int, plan_id: str, nonce: str = "") -> dict:
    plan = PLANS.get(plan_id)
    if plan is None:
        raise ValueError("unknown plan")
    suffix = f"_{nonce}" if nonce else ""
    return {
        "checkout_id": f"chk_{user_id}_{plan_id}{suffix}",
        "plan_id": plan_id,
        "status": "pending",
        "provider": "mock",
        "amount_cents": plan["amount_cents"],
        "currency": plan["currency"],
    }


def apply_provider_event(subscription: dict, event: dict) -> dict:
    """Apply a mock provider event. Active subscriptions stay active."""
    if event.get("type") != "checkout.completed":
        raise ValueError("unsupported event")
    if event.get("checkout_id") != subscription.get("checkout_id"):
        raise ValueError("checkout mismatch")
    updated = dict(subscription)
    updated["status"] = "active"
    updated["provider"] = "mock"
    return updated
