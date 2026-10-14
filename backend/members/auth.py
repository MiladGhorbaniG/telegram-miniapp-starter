from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from booknook_core.initdata import InvalidInitData, validate_init_data
from members.models import TelegramUser


class TelegramAuthentication(BaseAuthentication):
    """Accept Telegram initData, or the demo header when ALLOW_DEV_AUTH is on."""

    def authenticate_header(self, request) -> str:
        return "TMA"

    def authenticate(self, request):
        if settings.ALLOW_DEV_AUTH:
            raw = request.headers.get("X-Dev-User", "")
            if raw:
                try:
                    telegram_id = int(raw)
                except ValueError as exc:
                    raise AuthenticationFailed("dev user id is not an integer") from exc
                user, _ = TelegramUser.objects.get_or_create(
                    telegram_id=telegram_id,
                    defaults={"first_name": "Demo", "username": "demo"},
                )
                return (user, "dev")

        header = request.headers.get("Authorization", "")
        if not header.startswith("TMA "):
            raise AuthenticationFailed("missing Telegram init data")
        try:
            parsed = validate_init_data(
                header[4:].strip(),
                settings.TELEGRAM_BOT_TOKEN,
            )
        except InvalidInitData as exc:
            raise AuthenticationFailed(str(exc)) from exc
        profile = parsed["user"]
        user, _ = TelegramUser.objects.get_or_create(
            telegram_id=profile["id"],
            defaults={
                "first_name": profile.get("first_name", ""),
                "username": profile.get("username", ""),
            },
        )
        return (user, "tma")
