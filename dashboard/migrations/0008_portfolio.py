from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dashboard", "0007_add_updated_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="Portfolio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="Portfolio name")),
                ("description", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolios", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Portfolio",
                "verbose_name_plural": "Portfolios",
                "ordering": ["-updated_at"],
                "unique_together": {("user", "name")},
            },
        ),
        migrations.CreateModel(
            name="PortfolioItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.FloatField(default=0.0, verbose_name="Quantity")),
                ("avg_price", models.FloatField(default=0.0, verbose_name="Average price")),
                ("portfolio", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="dashboard.portfolio")),
                ("share", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_items", to="dashboard.share")),
            ],
            options={
                "verbose_name": "Portfolio position",
                "verbose_name_plural": "Portfolio positions",
                "unique_together": {("portfolio", "share")},
            },
        ),
        migrations.CreateModel(
            name="PortfolioTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("side", models.CharField(choices=[("buy", "Buy"), ("sell", "Sell")], max_length=4)),
                ("quantity", models.FloatField()),
                ("price", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.CharField(blank=True, default="", max_length=255)),
                ("portfolio", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="dashboard.portfolio")),
                ("share", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="dashboard.share")),
            ],
            options={
                "verbose_name": "Portfolio transaction",
                "verbose_name_plural": "Portfolio transactions",
                "ordering": ["-created_at"],
            },
        ),
    ]
