from datetime import timedelta

from config.settings import TINKOFF_TOKEN, logger
from dashboard.services.invest_client import (
    get_candle_interval,
    get_client_class,
    is_sdk_available,
    quotation_to_float,
    sdk_now,
)


def get_graph_from_history(share, days: int = 180):
    """График из локальной истории цен (без API)."""
    from dashboard.models import PriceHistory
    from django.utils import timezone

    since = timezone.now() - timedelta(days=days)
    history = (
        PriceHistory.objects.filter(share=share, recorded_at__gte=since)
        .order_by("recorded_at")
    )
    if not history.exists():
        return None

    try:
        from plotly.graph_objs import Scatter
        from plotly.offline import plot
    except ImportError:
        return "<p class='text-muted'>plotly не установлен</p>"

    x_data = [h.recorded_at for h in history]
    y_data = [h.price for h in history]
    return plot(
        [
            Scatter(
                x=x_data,
                y=y_data,
                mode="lines+markers",
                name=share.ticker,
                line=dict(color="#198754"),
            )
        ],
        output_type="div",
        include_plotlyjs="cdn",
    )


def get_graph(share, days: int = 180):
    """
    Построить график.
    1) Если есть TOKEN и SDK — берём свечи из API.
    2) Иначе — из локальной PriceHistory.
    """
    # Сначала пробуем локальную историю (всегда доступна без токена)
    local = get_graph_from_history(share, days=days)
    if local:
        return local

    if not TINKOFF_TOKEN or not is_sdk_available():
        return (
            "<p class='text-muted'>"
            "Нет данных для графика. "
            "Запустите <code>python manage.py seed_demo</code> "
            "или укажите TINKOFF_TOKEN и установите SDK."
            "</p>"
        )

    Client = get_client_class()
    CandleInterval = get_candle_interval()

    try:
        from plotly.graph_objs import Scatter
        from plotly.offline import plot

        with Client(TINKOFF_TOKEN) as client:
            x_data, y_data = [], []
            # get_all_candles может отсутствовать в новых версиях — fallback на get_candles
            try:
                candles_iter = client.get_all_candles(
                    figi=share.figi,
                    from_=sdk_now() - timedelta(days=days),
                    interval=CandleInterval.CANDLE_INTERVAL_DAY,
                )
            except AttributeError:
                resp = client.market_data.get_candles(
                    figi=share.figi,
                    from_=sdk_now() - timedelta(days=days),
                    to=sdk_now(),
                    interval=CandleInterval.CANDLE_INTERVAL_DAY,
                )
                candles_iter = resp.candles

            for candle in candles_iter:
                x_data.append(candle.time.date() if hasattr(candle.time, "date") else candle.time)
                y_data.append(quotation_to_float(candle.close))

        if not x_data:
            return "<p class='text-muted'>Нет данных свечей от API</p>"

        return plot(
            [
                Scatter(
                    x=x_data,
                    y=y_data,
                    mode="lines",
                    name=share.ticker,
                    opacity=0.85,
                    line=dict(color="#0d6efd", width=2),
                )
            ],
            output_type="div",
            include_plotlyjs="cdn",
        )
    except Exception as e:
        logger.error(f"Error building graph for {share.ticker}: {e}")
        return f"<p class='text-danger'>Ошибка построения графика: {e}</p>"
