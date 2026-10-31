from django.db import models


class Share(models.Model):
    """Акция"""

    figi = models.CharField(max_length=255, unique=True)
    isin = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name="Наименование компании")
    ticker = models.CharField(max_length=10, unique=True, verbose_name="Тикер")
    currency = models.CharField(max_length=20, verbose_name="Валюта")
    uid = models.CharField(max_length=255, unique=True)
    last_price = models.FloatField(blank=True, null=True, verbose_name="Текущая цена")
    is_trend_high = models.BooleanField(
        blank=True, null=True, verbose_name="Растет цена"
    )
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ["name"]

    def __str__(self):
        return f"{self.ticker} — {self.name}"


class PriceHistory(models.Model):
    """История изменения рыночных цен акций"""

    share = models.ForeignKey(
        Share, on_delete=models.CASCADE, related_name="price_history", verbose_name="Акция"
    )
    price = models.FloatField(verbose_name="Цена")
    recorded_at = models.DateTimeField(verbose_name="Время записи", db_index=True)
    source = models.CharField(
        max_length=32, default="tinkoff", verbose_name="Источник"
    )

    class Meta:
        verbose_name = "Запись истории цены"
        verbose_name_plural = "История цен"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["share", "-recorded_at"]),
        ]
        # Избегаем дублирования одной и той же цены в одну минуту
        unique_together = [("share", "recorded_at")]

    def __str__(self):
        return f"{self.share.ticker}: {self.price} @ {self.recorded_at}"
