import hmac
import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from billing.models import Subscription
from billing.tasks import prepare_receipt
from booknook_core.billing import PLANS, apply_provider_event, start_checkout
from members.auth import TelegramAuthentication


def serialize(subscription: Subscription) -> dict:
    return {
        "checkout_id": subscription.checkout_id,
        "plan_id": subscription.plan_id,
        "status": subscription.status,
        "amount_cents": subscription.amount_cents,
        "receipt_ready": subscription.receipt_ready,
        "receipt_note": subscription.receipt_note,
    }


def activate(subscription: Subscription) -> Subscription:
    updated = apply_provider_event(
        {"checkout_id": subscription.checkout_id, "status": subscription.status},
        {"type": "checkout.completed", "checkout_id": subscription.checkout_id},
    )
    subscription.status = updated["status"]
    subscription.save(update_fields=["status"])
    prepare_receipt.delay(subscription.id)
    subscription.refresh_from_db()
    return subscription


@api_view(["GET"])
def plans(request):
    return Response(list(PLANS.values()))


@api_view(["POST"])
@authentication_classes([TelegramAuthentication])
def checkout(request):
    user = request.user
    try:
        started = start_checkout(
            user.telegram_id,
            request.data.get("plan_id", ""),
            nonce=uuid.uuid4().hex[:8],
        )
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc
    subscription = Subscription.objects.create(
        user=user,
        plan_id=started["plan_id"],
        status=started["status"],
        checkout_id=started["checkout_id"],
        amount_cents=started["amount_cents"],
    )
    return Response(serialize(subscription), status=201)


@api_view(["POST"])
@authentication_classes([TelegramAuthentication])
def confirm(request):
    user = request.user
    subscription = get_object_or_404(
        Subscription,
        user=user,
        checkout_id=request.data.get("checkout_id", ""),
    )
    return Response(serialize(activate(subscription)))


@api_view(["POST"])
def webhook(request):
    secret = request.headers.get("X-Mock-Signature", "")
    if not hmac.compare_digest(secret, settings.MOCK_PAY_SECRET):
        return Response({"detail": "bad signature"}, status=403)
    checkout_id = request.data.get("checkout_id", "")
    subscription = Subscription.objects.filter(checkout_id=checkout_id).first()
    if subscription is None:
        return Response({"detail": "unknown checkout"}, status=404)
    try:
        updated = apply_provider_event(
            {"checkout_id": subscription.checkout_id, "status": subscription.status},
            {
                "type": request.data.get("type", ""),
                "checkout_id": request.data.get("checkout_id", ""),
            },
        )
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    subscription.status = updated["status"]
    subscription.save(update_fields=["status"])
    prepare_receipt.delay(subscription.id)
    subscription.refresh_from_db()
    return Response(serialize(subscription))


@api_view(["GET"])
@authentication_classes([TelegramAuthentication])
def current(request):
    user = request.user
    subscription = user.subscriptions.order_by("-created_at").first()
    if subscription is None:
        return Response({"subscription": None})
    return Response({"subscription": serialize(subscription)})
