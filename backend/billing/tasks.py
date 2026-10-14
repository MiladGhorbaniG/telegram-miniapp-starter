from billing.models import Subscription
from config.celery import app


@app.task
def prepare_receipt(subscription_id: int) -> str:
    subscription = Subscription.objects.get(pk=subscription_id)
    subscription.receipt_ready = True
    subscription.receipt_note = f"BookNook receipt for {subscription.plan_id}"
    subscription.save(update_fields=["receipt_ready", "receipt_note"])
    return subscription.receipt_note
