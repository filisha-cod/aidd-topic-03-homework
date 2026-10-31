"""Seed demo shares so the app works without TINKOFF_TOKEN. Agent B variant."""
from django.core.management.base import BaseCommand

from dashboard.models import Share

DEMO_SHARES = [
    dict(figi="BBG004730N88", isin="RU0009029540", name="Сбер Банк", ticker="SBER",
         currency="rub", uid="e6123145-9665-43e0-8413-cd61b8aa9b13", last_price=280.5, is_trend_high=True),
    dict(figi="BBG004731354", isin="RU0007288411", name="Газпром", ticker="GAZP",
         currency="rub", uid="962e2a95-3e4e-4a74-ad5d-b679484747d8", last_price=165.2, is_trend_high=False),
    dict(figi="BBG004S681W1", isin="RU000A0JP5V6", name="Яндекс", ticker="YNDX",
         currency="rub", uid="10e17a87-3bce-4a09-9b28-0b998a481612", last_price=4120.0, is_trend_high=True),
    dict(figi="BBG004730RP0", isin="RU0007661625", name="ЛУКОЙЛ", ticker="LKOH",
         currency="rub", uid="02cfdf26-7c5b-4c0f-8e8a-0a2f0f2e2c3d", last_price=6850.0, is_trend_high=True),
    dict(figi="BBG000B9XRY4", isin="US0378331005", name="Apple Inc", ticker="AAPL",
         currency="usd", uid="a1b2c3d4-e5f6-7890-abcd-ef1234567890", last_price=178.25, is_trend_high=False),
]


class Command(BaseCommand):
    help = "Load demo shares (no API token required)"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear shares first")

    def handle(self, *args, **options):
        if options["clear"]:
            Share.objects.all().delete()
            self.stdout.write("Cleared shares")

        n = 0
        for data in DEMO_SHARES:
            _, created = Share.objects.update_or_create(
                figi=data["figi"],
                defaults={k: v for k, v in data.items() if k != "figi"},
            )
            if created:
                n += 1
        self.stdout.write(self.style.SUCCESS(f"Shares ready. Newly created: {n}"))
