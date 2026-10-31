from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0007_add_updated_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="PriceHistory",
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
                ("price", models.FloatField(verbose_name="Цена")),
                ("recorded_at", models.DateTimeField(db_index=True, verbose_name="Время записи")),
                (
                    "source",
                    models.CharField(
                        default="tinkoff", max_length=32, verbose_name="Источник"
                    ),
                ),
                (
                    "share",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_history",
                        to="dashboard.share",
                        verbose_name="Акция",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запись истории цены",
                "verbose_name_plural": "История цен",
                "ordering": ["-recorded_at"],
                "unique_together": {("share", "recorded_at")},
            },
        ),
        migrations.AddIndex(
            model_name="pricehistory",
            index=models.Index(
                fields=["share", "-recorded_at"], name="dashboard_p_share_i_idx"
            ),
        ),
    ]
