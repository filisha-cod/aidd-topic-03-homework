from config.settings import TINKOFF_TOKEN, logger
from dashboard.services.invest_client import (
    get_client_class,
    is_sdk_available,
    quotation_to_float,
)


def get_last_data(share):
    """Получить последнюю цену и время для акции через T-Invest API."""
    if not TINKOFF_TOKEN:
        logger.warning("TINKOFF_TOKEN is empty, skipping market data request")
        return None, None

    if not is_sdk_available():
        logger.error("T-Invest SDK is not installed (t-tech-investments or tinkoff-investments)")
        return None, None

    Client = get_client_class()
    try:
        with Client(TINKOFF_TOKEN) as client:
            resp = client.market_data.get_last_prices(figi=[share.figi])
            if not resp.last_prices:
                logger.warning(f"No last price for FIGI {share.figi}")
                return None, None
            last = resp.last_prices[0]
            price = quotation_to_float(last.price)
            logger.info(f"Get last data for share id={share.id} ticker={share.ticker}: {price}")
            return price, last.time
    except Exception as e:
        logger.error(f"Error getting last data for {share.ticker}: {e}")
        return None, None
