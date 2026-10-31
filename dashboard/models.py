"""
Models for Investing Demo application.
Agent B implementation notes:
- Share is the core instrument entity (kept from original).
- Portfolio / PortfolioItem / PortfolioTransaction implement virtual portfolio feature.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum, F


class Share(models.Model):
    """Stock / equity instrument."""

    figi = models.CharField(max_length=255, unique=True)
    isin = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name="Company name")
    ticker = models.CharField(max_length=10, unique=True, verbose_name="Ticker")
    currency = models.CharField(max_length=20, verbose_name="Currency")
    uid = models.CharField(max_length=255, unique=True)
    last_price = models.FloatField(blank=True, null=True, verbose_name="Last price")
    is_trend_high = models.BooleanField(blank=True, null=True, verbose_name="Price is rising")
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Share"
        verbose_name_plural = "Shares"
        ordering = ["name"]

    def __str__(self):
        return f"{self.ticker} ({self.name})"


class Portfolio(models.Model):
    """User virtual investment portfolio."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios",
    )
    name = models.CharField(max_length=120, verbose_name="Portfolio name")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"
        ordering = ["-updated_at"]
        unique_together = [("user", "name")]

    def __str__(self):
        return f"{self.name} ({self.user})"

    def total_cost_basis(self) -> float:
        """Sum of qty * avg_price across positions."""
        total = 0.0
        for item in self.items.select_related("share").all():
            total += item.quantity * item.avg_price
        return round(total, 2)

    def total_market_value(self) -> float:
        """Current market value of the portfolio."""
        total = 0.0
        for item in self.items.select_related("share").all():
            price = item.share.last_price or item.avg_price
            total += item.quantity * price
        return round(total, 2)

    def total_pnl(self) -> float:
        return round(self.total_market_value() - self.total_cost_basis(), 2)

    def total_pnl_percent(self) -> float:
        basis = self.total_cost_basis()
        if not basis:
            return 0.0
        return round((self.total_pnl() / basis) * 100, 2)


class PortfolioItem(models.Model):
    """Position inside a portfolio (quantity + average purchase price)."""

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="items"
    )
    share = models.ForeignKey(Share, on_delete=models.CASCADE, related_name="portfolio_items")
    quantity = models.FloatField(default=0.0, verbose_name="Quantity")
    avg_price = models.FloatField(default=0.0, verbose_name="Average price")

    class Meta:
        verbose_name = "Portfolio position"
        verbose_name_plural = "Portfolio positions"
        unique_together = [("portfolio", "share")]

    def __str__(self):
        return f"{self.share.ticker} x {self.quantity}"

    @property
    def market_value(self) -> float:
        price = self.share.last_price if self.share.last_price is not None else self.avg_price
        return round(self.quantity * price, 2)

    @property
    def cost_basis(self) -> float:
        return round(self.quantity * self.avg_price, 2)

    @property
    def pnl(self) -> float:
        return round(self.market_value - self.cost_basis, 2)


class PortfolioTransaction(models.Model):
    """Buy / sell operation log."""

    BUY = "buy"
    SELL = "sell"
    SIDE_CHOICES = [(BUY, "Buy"), (SELL, "Sell")]

    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="transactions"
    )
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.FloatField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "Portfolio transaction"
        verbose_name_plural = "Portfolio transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.side.upper()} {self.quantity} {self.share.ticker} @ {self.price}"

    @property
    def amount(self) -> float:
        return round(self.quantity * self.price, 2)
