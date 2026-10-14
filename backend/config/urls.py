from django.urls import path

from billing.views import checkout, confirm, current, plans, webhook
from faqdesk.views import faq
from members.views import health, me

urlpatterns = [
    path("api/health", health),
    path("api/me", me),
    path("api/plans", plans),
    path("api/subscriptions/checkout", checkout),
    path("api/subscriptions/confirm", confirm),
    path("api/subscriptions/webhook", webhook),
    path("api/subscriptions/current", current),
    path("api/faq", faq),
]
