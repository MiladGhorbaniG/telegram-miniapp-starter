import json
from pathlib import Path

from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from booknook_core.faq import MockFaqModel, answer_faq
from members.auth import TelegramAuthentication


@api_view(["POST"])
@authentication_classes([TelegramAuthentication])
def faq(request):
    question = str(request.data.get("question") or "").strip()
    if not question:
        raise ValidationError("question is empty")
    entries = json.loads(Path(settings.FAQ_PATH).read_text(encoding="utf-8"))
    return Response(answer_faq(question, entries, MockFaqModel()))
