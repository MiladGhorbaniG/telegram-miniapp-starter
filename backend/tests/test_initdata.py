from __future__ import annotations

import json

import pytest

from booknook_core.initdata import InvalidInitData, sign_init_data, validate_init_data

TOKEN = "123456:booknook-demo"


def _fields() -> dict[str, str]:
    return {
        "auth_date": "1700000000",
        "query_id": "AAE",
        "user": json.dumps(
            {"id": 42, "first_name": "Ada", "username": "ada"},
            separators=(",", ":"),
        ),
    }


def test_round_trip() -> None:
    signed = sign_init_data(_fields(), TOKEN)
    parsed = validate_init_data(signed, TOKEN, now=1700000100)
    assert parsed["user"]["id"] == 42
    assert parsed["user"]["first_name"] == "Ada"
    assert parsed["query_id"] == "AAE"


def test_bad_hash() -> None:
    with pytest.raises(InvalidInitData, match="bad hash"):
        validate_init_data("auth_date=1700000000&user=%7B%7D&hash=deadbeef", TOKEN, now=1700000000)


def test_expired() -> None:
    signed = sign_init_data(_fields(), TOKEN)
    with pytest.raises(InvalidInitData, match="expired"):
        validate_init_data(signed, TOKEN, max_age_seconds=10, now=1700001000)


def test_empty_token() -> None:
    with pytest.raises(InvalidInitData, match="bot token"):
        validate_init_data("hash=abc", "", now=1)
