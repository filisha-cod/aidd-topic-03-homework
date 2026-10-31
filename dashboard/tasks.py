"""Celery tasks. Agent B: price update only (portfolio is interactive)."""
from config.settings import logger
from dashboard.models import Share

try:
    from config.celery import app
except ImportError:
    class _Dummy:
        def task(self, *a, **k):
            def deco(fn):
                return fn
            return deco
    app = _Dummy()


@app.task(bind=True, max_retries=3)
def update_last_price(self=None):
    from dashboard.services.market_data import get_last_data

    updated = 0
    for share in Share.objects.all():
        try:
            last_price, _ = get_last_data(share)
            if last_price is None:
                continue
            is_trend_high = True
            if share.last_price is not None:
                is_trend_high = last_price >= share.last_price
            Share.objects.filter(id=share.id).update(
                last_price=last_price, is_trend_high=is_trend_high
            )
            updated += 1
        except Exception as e:
            logger.error("update_last_price %s: %s", share.ticker, e)
    logger.info("update_last_price: %s shares", updated)
    return updated
