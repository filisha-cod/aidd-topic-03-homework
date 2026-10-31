"""
Business logic for virtual portfolio operations.
Agent B: keep service layer thin and explicit.
"""
from django.db import transaction

from dashboard.models import Portfolio, PortfolioItem, PortfolioTransaction, Share


class PortfolioError(Exception):
    pass


@transaction.atomic
def execute_buy(portfolio: Portfolio, share: Share, quantity: float, price: float, note: str = ""):
    if quantity <= 0 or price < 0:
        raise PortfolioError("Quantity must be > 0 and price >= 0")

    item, created = PortfolioItem.objects.get_or_create(
        portfolio=portfolio,
        share=share,
        defaults={"quantity": 0.0, "avg_price": 0.0},
    )

    old_qty = item.quantity
    old_avg = item.avg_price
    new_qty = old_qty + quantity
    if new_qty <= 0:
        raise PortfolioError("Invalid resulting quantity")

    # weighted average price
    item.avg_price = ((old_qty * old_avg) + (quantity * price)) / new_qty
    item.quantity = new_qty
    item.save()

    PortfolioTransaction.objects.create(
        portfolio=portfolio,
        share=share,
        side=PortfolioTransaction.BUY,
        quantity=quantity,
        price=price,
        note=note,
    )
    return item


@transaction.atomic
def execute_sell(portfolio: Portfolio, share: Share, quantity: float, price: float, note: str = ""):
    if quantity <= 0 or price < 0:
        raise PortfolioError("Quantity must be > 0 and price >= 0")

    try:
        item = PortfolioItem.objects.get(portfolio=portfolio, share=share)
    except PortfolioItem.DoesNotExist:
        raise PortfolioError("No position to sell")

    if quantity > item.quantity:
        raise PortfolioError(f"Not enough shares: have {item.quantity}, trying to sell {quantity}")

    item.quantity = item.quantity - quantity
    if item.quantity == 0:
        item.delete()
    else:
        item.save()

    PortfolioTransaction.objects.create(
        portfolio=portfolio,
        share=share,
        side=PortfolioTransaction.SELL,
        quantity=quantity,
        price=price,
        note=note,
    )
    return True
