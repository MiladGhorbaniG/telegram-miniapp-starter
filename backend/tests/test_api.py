from __future__ import annotations

import json
import time

import pytest
from booknook_core.initdata import sign_init_data

TOKEN = "123456:booknook-demo"


@pytest.fixture(autouse=True)
def bot_token(settings):
    settings.TELEGRAM_BOT_TOKEN = TOKEN
    settings.ALLOW_DEV_AUTH = True
    settings.MOCK_PAY_SECRET = "booknook-mock"


def _signed_header() -> dict[str, str]:
    init_data = sign_init_data(
        {
            "auth_date": str(int(time.time())),
            "user": json.dumps(
                {"id": 42, "first_name": "Ada", "username": "ada"},
                separators=(",", ":"),
            ),
        },
        TOKEN,
    )
    return {"HTTP_AUTHORIZATION": f"TMA {init_data}"}


@pytest.mark.django_db
def test_dev_user_can_subscribe_and_get_a_receipt(client, settings):
    from config.celery import app as celery_app

    settings.CELERY_TASK_ALWAYS_EAGER = True
    celery_app.conf.task_always_eager = True
    headers = {"HTTP_X_DEV_USER": "1001"}
    me = client.get("/api/me", **headers)
    assert me.status_code == 200
    assert me.json()["username"] == "demo"

    plans = client.get("/api/plans")
    assert plans.json()[0]["id"] == "reading-room"

    checkout = client.post(
        "/api/subscriptions/checkout",
        data=json.dumps({"plan_id": "reading-room"}),
        content_type="application/json",
        **headers,
    )
    assert checkout.status_code == 201
    checkout_id = checkout.json()["checkout_id"]
    assert checkout.json()["status"] == "pending"

    confirmed = client.post(
        "/api/subscriptions/confirm",
        data=json.dumps({"checkout_id": checkout_id}),
        content_type="application/json",
        **headers,
    )
    body = confirmed.json()
    assert body["status"] == "active"
    assert body["receipt_ready"] is True
    assert "reading-room" in body["receipt_note"]


@pytest.mark.django_db
def test_webhook_checks_the_mock_signature(client):
    from config.celery import app as celery_app

    celery_app.conf.task_always_eager = True
    headers = {"HTTP_X_DEV_USER": "1002"}
    checkout = client.post(
        "/api/subscriptions/checkout",
        data=json.dumps({"plan_id": "reading-room"}),
        content_type="application/json",
        **headers,
    )
    checkout_id = checkout.json()["checkout_id"]
    rejected = client.post(
        "/api/subscriptions/webhook",
        data=json.dumps({"type": "checkout.completed", "checkout_id": checkout_id}),
        content_type="application/json",
    )
    assert rejected.status_code == 403
    accepted = client.post(
        "/api/subscriptions/webhook",
        data=json.dumps({"type": "checkout.completed", "checkout_id": checkout_id}),
        content_type="application/json",
        HTTP_X_MOCK_SIGNATURE="booknook-mock",
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "active"
    assert accepted.json()["receipt_ready"] is True


@pytest.mark.django_db
def test_telegram_init_data_and_faq(client):
    me = client.get("/api/me", **_signed_header())
    assert me.status_code == 200
    assert me.json()["first_name"] == "Ada"
    faq = client.post(
        "/api/faq",
        data=json.dumps({"question": "What is the late fee?"}),
        content_type="application/json",
        **_signed_header(),
    )
    assert faq.status_code == 200
    assert "book credit" in faq.json()["answer"]
    assert "late-fee" in faq.json()["sources"]


@pytest.mark.django_db
def test_missing_auth_is_rejected(client, settings):
    settings.ALLOW_DEV_AUTH = False
    response = client.get("/api/me")
    assert response.status_code == 401
