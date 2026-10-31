from datetime import datetime, timezone

from config.settings import logger
from dashboard.models import PriceHistory, Share

try:
    from config.celery import app
except ImportError:
    class _DummyApp:
        def task(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
    app = _DummyApp()


@app.task(bind=True, max_retries=3)
def update_last_price(self=None):
    """Обновить last_price и is_trend_high для всех акций."""
    from dashboard.services.market_data import get_last_data

    shares = Share.objects.all()
    updated = 0

    for share in shares:
        try:
            last_price, price_time = get_last_data(share)
            if last_price is None:
                continue

            is_trend_high = True
            if share.last_price is not None:
                is_trend_high = last_price >= share.last_price

            Share.objects.filter(id=share.id).update(
                last_price=last_price,
                is_trend_high=is_trend_high,
            )
            updated += 1
        except Exception as e:
            logger.error(f"Failed to update price for share {share.id} ({share.ticker}): {e}")

    logger.info(f"update_last_price finished: {updated}/{shares.count()} shares updated")
    return updated


@app.task(bind=True, max_retries=3)
def save_price_history(self=None):
    """Сохранить текущие цены в историю (без дублирования одной и той же минуты)."""
    shares = Share.objects.exclude(last_price__isnull=True)
    created = 0
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    for share in shares:
        try:
            exists = PriceHistory.objects.filter(
                share=share, recorded_at=now
            ).exists()
            if exists:
                continue

            PriceHistory.objects.create(
                share=share,
                price=share.last_price,
                recorded_at=now,
                source="api",
            )
            created += 1
        except Exception as e:
            logger.error(f"Failed to save history for {share.ticker}: {e}")

    logger.info(f"save_price_history finished: {created} new records")
    return created
