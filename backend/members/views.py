from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from members.auth import TelegramAuthentication


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "service": "booknook-desk"})


@api_view(["GET"])
@authentication_classes([TelegramAuthentication])
def me(request):
    user = request.user
    return Response(
        {
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "username": user.username,
        }
    )
