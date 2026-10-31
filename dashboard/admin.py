from django.contrib import admin

from dashboard.models import Portfolio, PortfolioItem, PortfolioTransaction, Share


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "last_price", "is_trend_high", "currency", "updated_at")
    search_fields = ("figi", "isin", "name", "ticker")
    list_filter = ("currency", "is_trend_high")


class PortfolioItemInline(admin.TabularInline):
    model = PortfolioItem
    extra = 0
    raw_id_fields = ("share",)


class PortfolioTransactionInline(admin.TabularInline):
    model = PortfolioTransaction
    extra = 0
    raw_id_fields = ("share",)
    readonly_fields = ("created_at",)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "updated_at")
    search_fields = ("name", "user__username", "user__email")
    inlines = [PortfolioItemInline, PortfolioTransactionInline]


@admin.register(PortfolioTransaction)
class PortfolioTransactionAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "side", "share", "quantity", "price", "created_at")
    list_filter = ("side",)
