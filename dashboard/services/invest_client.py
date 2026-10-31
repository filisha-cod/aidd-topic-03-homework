"""
Совместимый слой для T-Invest SDK.
Поддерживает:
  - t-tech-investments  →  from t_tech.invest import Client
  - старый tinkoff-investments → from tinkoff.invest import Client
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

# ---------------------------------------------------------------------------
# Попытка импорта нового и старого SDK
# ---------------------------------------------------------------------------
_Client = None
_CandleInterval = None
_quotation_to_decimal = None
_now_fn = None
_sdk_name = None

try:
    from t_tech.invest import Client as _Client
    from t_tech.invest import CandleInterval as _CandleInterval
    from t_tech.invest.utils import quotation_to_decimal as _quotation_to_decimal
    from t_tech.invest.utils import now as _now_fn
    _sdk_name = "t_tech"
except ImportError:
    try:
        from tinkoff.invest import Client as _Client
        from tinkoff.invest import CandleInterval as _CandleInterval
        from tinkoff.invest.utils import quotation_to_decimal as _quotation_to_decimal
        from tinkoff.invest.utils import now as _now_fn
        _sdk_name = "tinkoff"
    except ImportError:
        pass


def is_sdk_available() -> bool:
    return _Client is not None


def get_sdk_name() -> Optional[str]:
    return _sdk_name


def get_client_class():
    return _Client


def get_candle_interval():
    return _CandleInterval


def quotation_to_float(quotation) -> float:
    if quotation is None:
        return 0.0
    if _quotation_to_decimal is not None:
        try:
            return float(_quotation_to_decimal(quotation))
        except Exception:
            pass
    try:
        units = getattr(quotation, "units", 0) or 0
        nano = getattr(quotation, "nano", 0) or 0
        return float(units) + float(nano) / 1e9
    except Exception:
        return 0.0


def sdk_now():
    if _now_fn is not None:
        return _now_fn()
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
