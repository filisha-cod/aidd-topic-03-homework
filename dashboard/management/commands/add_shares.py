from django.core.management.base import BaseCommand

from config.settings import TINKOFF_TOKEN, logger
from dashboard.models import Share
from dashboard.services.invest_client import get_client_class, is_sdk_available, get_sdk_name


class Command(BaseCommand):
    help = "Add shares to DB from T-Invest API"

    def handle(self, *args, **options):
        if not TINKOFF_TOKEN:
            self.stderr.write(
                self.style.ERROR(
                    "TINKOFF_TOKEN is empty.\n"
                    "Either set it in .env, or use demo data:\n"
                    "  python manage.py seed_demo"
                )
            )
            return

        if not is_sdk_available():
            self.stderr.write(
                self.style.ERROR(
                    "T-Invest SDK is not installed.\n"
                    "Install:\n"
                    "  pip install t-tech-investments --index-url https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple\n"
                    "Or use demo data without API:\n"
                    "  python manage.py seed_demo"
                )
            )
            return

        Client = get_client_class()
        self.stdout.write(f"Using SDK: {get_sdk_name()}")

        created = 0
        updated = 0
        try:
            with Client(TINKOFF_TOKEN) as client:
                shares = client.instruments.shares()
                for share in shares.instruments:
                    currency = share.currency
                    if hasattr(currency, "name"):
                        currency = currency.name
                    else:
                        currency = str(currency)

                    obj, was_created = Share.objects.update_or_create(
                        figi=share.figi,
                        defaults={
                            "name": share.name,
                            "isin": share.isin,
                            "ticker": share.ticker,
                            "currency": currency,
                            "uid": share.uid,
                        },
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
        except Exception as e:
            logger.error(f"add_shares failed: {e}")
            self.stderr.write(self.style.ERROR(str(e)))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created: {created}, updated: {updated}")
        )
