"""Chart helpers. Agent B uses Plotly offline plots."""
from datetime import timedelta

from config.settings import TINKOFF_TOKEN, logger
from dashboard.services.invest_client import (
    get_candle_interval,
    get_client_class,
    is_sdk_available,
    quotation_to_float,
    sdk_now,
)


def get_graph(share, days: int = 180):
    """Build price chart from T-Invest API when available."""
    if not TINKOFF_TOKEN or not is_sdk_available():
        return (
            "<p class='text-muted'>"
            "Chart unavailable: set TINKOFF_TOKEN and install t-tech-investments, "
            "or use demo prices from seed_demo."
            "</p>"
        )

    Client = get_client_class()
    CandleInterval = get_candle_interval()

    try:
        from plotly.graph_objs import Scatter
        from plotly.offline import plot

        with Client(TINKOFF_TOKEN) as client:
            x_data, y_data = [], []
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
                t = candle.time
                x_data.append(t.date() if hasattr(t, "date") else t)
                y_data.append(quotation_to_float(candle.close))

        if not x_data:
            return "<p class='text-muted'>No candle data from API</p>"

        return plot(
            [
                Scatter(
                    x=x_data,
                    y=y_data,
                    mode="lines",
                    name=share.ticker,
                    line=dict(color="#0d6efd", width=2),
                )
            ],
            output_type="div",
            include_plotlyjs="cdn",
        )
    except Exception as e:
        logger.error("graph error for %s: %s", share.ticker, e)
        return f"<p class='text-danger'>Chart error: {e}</p>"
