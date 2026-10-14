from __future__ import annotations

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, urlencode


class InvalidInitData(ValueError):
    """Telegram initData failed validation."""


def sign_init_data(fields: dict[str, str], bot_token: str) -> str:
    """Build a signed initData query string the same way validation reads it.

    Useful for tests and local fixtures. Telegram itself creates the real string.
    """
    check_string = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    digest = _sign(check_string, bot_token)
    return urlencode({**fields, "hash": digest})


def validate_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age_seconds: int = 86_400,
    now: int | None = None,
) -> dict:
    """Validate Mini App initData using Telegram's WebAppData HMAC construction."""
    if not bot_token:
        raise InvalidInitData("bot token is empty")
    data = {key: value for key, value in parse_qsl(init_data, keep_blank_values=True)}
    received = data.pop("hash", "")
    if not received:
        raise InvalidInitData("missing hash")
    check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    calculated = _sign(check_string, bot_token)
    if not hmac.compare_digest(calculated, received):
        raise InvalidInitData("bad hash")
    try:
        auth_date = int(data.get("auth_date", "0"))
    except ValueError as exc:
        raise InvalidInitData("bad auth_date") from exc
    current = int(time.time()) if now is None else now
    if current - auth_date > max_age_seconds:
        raise InvalidInitData("init data expired")
    if "user" not in data:
        raise InvalidInitData("missing user")
    try:
        user = json.loads(data["user"])
    except json.JSONDecodeError as exc:
        raise InvalidInitData("user is not json") from exc
    if "id" not in user:
        raise InvalidInitData("user has no id")
    return {"user": user, "auth_date": auth_date, "query_id": data.get("query_id", "")}


def _sign(check_string: str, bot_token: str) -> str:
    secret = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(secret, check_string.encode("utf-8"), hashlib.sha256).hexdigest()
