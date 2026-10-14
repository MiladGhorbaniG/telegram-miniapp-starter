from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("plan_id", models.CharField(max_length=40)),
                ("status", models.CharField(default="pending", max_length=20)),
                ("checkout_id", models.CharField(max_length=80, unique=True)),
                ("amount_cents", models.PositiveIntegerField()),
                ("receipt_ready", models.BooleanField(default=False)),
                ("receipt_note", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to="members.telegramuser",
                    ),
                ),
            ],
        ),
    ]
