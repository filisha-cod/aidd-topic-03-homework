"""
Заполнить БД демо-данными, чтобы приложение работало без TINKOFF_TOKEN.
"""
from datetime import datetime, timedelta, timezone
import random

from django.core.management.base import BaseCommand
from django.utils import timezone as dj_tz

from dashboard.models import PriceHistory, Share


DEMO_SHARES = [
    {
        "figi": "BBG004730N88",
        "isin": "RU0009029540",
        "name": "Сбер Банк",
        "ticker": "SBER",
        "currency": "rub",
        "uid": "e6123145-9665-43e0-8413-cd61b8aa9b13",
        "last_price": 280.50,
        "is_trend_high": True,
    },
    {
        "figi": "BBG004731354",
        "isin": "RU0007288411",
        "name": "Газпром",
        "ticker": "GAZP",
        "currency": "rub",
        "uid": "962e2a95-3e4e-4a74-ad5d-b679484747d8",
        "last_price": 165.20,
        "is_trend_high": False,
    },
    {
        "figi": "BBG004S681W1",
        "isin": "RU000A0JP5V6",
        "name": "Яндекс",
        "ticker": "YNDX",
        "currency": "rub",
        "uid": "10e17a87-3bce-4a09-9b28-0b998a481612",
        "last_price": 4120.00,
        "is_trend_high": True,
    },
    {
        "figi": "BBG004730RP0",
        "isin": "RU0007661625",
        "name": "ЛУКОЙЛ",
        "ticker": "LKOH",
        "currency": "rub",
        "uid": "02cfdf26-7c5b-4c0f-8e8a-0a2f0f2e2c3d",
        "last_price": 6850.00,
        "is_trend_high": True,
    },
    {
        "figi": "BBG000B9XRY4",
        "isin": "US0378331005",
        "name": "Apple Inc",
        "ticker": "AAPL",
        "currency": "usd",
        "uid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "last_price": 178.25,
        "is_trend_high": False,
    },
]


class Command(BaseCommand):
    help = "Seed demo shares and price history (works without TINKOFF_TOKEN)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="How many days of price history to generate (default: 30)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing shares and history before seeding",
        )

    def handle(self, *args, **options):
        days = options["days"]
        if options["clear"]:
            PriceHistory.objects.all().delete()
            Share.objects.all().delete()
            self.stdout.write("Cleared existing data")

        created_shares = 0
        for data in DEMO_SHARES:
            share, created = Share.objects.update_or_create(
                figi=data["figi"],
                defaults={
                    "isin": data["isin"],
                    "name": data["name"],
                    "ticker": data["ticker"],
                    "currency": data["currency"],
                    "uid": data["uid"],
                    "last_price": data["last_price"],
                    "is_trend_high": data["is_trend_high"],
                },
            )
            if created:
                created_shares += 1

            # Генерация истории цен
            base = data["last_price"]
            now = dj_tz.now().replace(hour=18, minute=0, second=0, microsecond=0)
            hist_created = 0
            for i in range(days, 0, -1):
                dt = now - timedelta(days=i)
                # небольшое случайное блуждание ±2%
                noise = 1 + random.uniform(-0.02, 0.02)
                price = round(base * (0.95 + 0.05 * (days - i) / days) * noise, 2)
                _, was_created = PriceHistory.objects.get_or_create(
                    share=share,
                    recorded_at=dt,
                    defaults={"price": price, "source": "demo"},
                )
                if was_created:
                    hist_created += 1

            self.stdout.write(
                f"  {share.ticker}: history points = {hist_created}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Shares created/updated: {len(DEMO_SHARES)} "
                f"(new: {created_shares}). History for {days} days."
            )
        )
