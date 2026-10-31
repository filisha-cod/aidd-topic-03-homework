from django.contrib import admin

from dashboard.models import PriceHistory, Share


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "last_price", "is_trend_high", "currency", "updated_at")
    search_fields = ("figi", "isin", "name", "ticker")
    list_filter = ("currency", "is_trend_high")
    readonly_fields = ("updated_at",)
    fields = (
        "figi",
        "isin",
        "name",
        "ticker",
        "currency",
        "uid",
        "last_price",
        "is_trend_high",
        "updated_at",
    )


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("share", "price", "recorded_at", "source")
    list_filter = ("source", "recorded_at")
    search_fields = ("share__ticker", "share__name")
    date_hierarchy = "recorded_at"
    raw_id_fields = ("share",)
