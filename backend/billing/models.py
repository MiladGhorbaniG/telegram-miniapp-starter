from django.db import models


class Subscription(models.Model):
    user = models.ForeignKey(
        "members.TelegramUser",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan_id = models.CharField(max_length=40)
    status = models.CharField(max_length=20, default="pending")
    checkout_id = models.CharField(max_length=80, unique=True)
    amount_cents = models.PositiveIntegerField()
    receipt_ready = models.BooleanField(default=False)
    receipt_note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
