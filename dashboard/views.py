from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Min
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, View, UpdateView

from .forms import ShareModelForm
from .models import PriceHistory, Share
from .services.graph import get_graph


class ShareListView(ListView):
    """Список акций"""

    model = Share
    template_name = "dashboard/list.html"
    paginate_by = 100
    context_object_name = "share_list"


class ShareDetailView(View):
    def get(self, request, pk):
        share = get_object_or_404(Share, id=pk)
        days = int(request.GET.get("days", 180))
        days = max(7, min(days, 365 * 2))

        return render(
            request,
            "dashboard/detail.html",
            {
                "plot_div": get_graph(share, days=days),
                "share": share,
                "days": days,
            },
        )


class ShareCreateView(LoginRequiredMixin, CreateView):
    """Добавление инструмента"""

    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")
    login_url = reverse_lazy("user:auth")


class ShareUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование инструмента"""

    model = Share
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")
    login_url = reverse_lazy("user:auth")


class ShareDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление акции"""

    model = Share
    template_name = "dashboard/delete.html"
    success_url = reverse_lazy("dashboard:index")
    login_url = reverse_lazy("user:auth")


class PriceHistoryView(View):
    """История изменения рыночных цен акции"""

    def get(self, request, pk):
        share = get_object_or_404(Share, id=pk)
        days = int(request.GET.get("days", 30))
        days = max(1, min(days, 365))

        since = timezone.now() - timedelta(days=days)
        history = (
            PriceHistory.objects.filter(share=share, recorded_at__gte=since)
            .order_by("recorded_at")
        )

        prices = list(history.values_list("price", flat=True))
        stats = {}
        if prices:
            first = prices[0]
            last = prices[-1]
            abs_change = last - first
            pct_change = (abs_change / first * 100) if first else 0
            stats = {
                "min": min(prices),
                "max": max(prices),
                "first": first,
                "last": last,
                "abs_change": round(abs_change, 4),
                "pct_change": round(pct_change, 2),
                "count": len(prices),
            }

        # Простой график из накопленных данных
        plot_div = None
        if history.exists():
            from plotly.graph_objs import Scatter
            from plotly.offline import plot

            x_data = [h.recorded_at for h in history]
            y_data = [h.price for h in history]
            plot_div = plot(
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

        return render(
            request,
            "dashboard/history.html",
            {
                "share": share,
                "history": history,
                "stats": stats,
                "days": days,
                "plot_div": plot_div,
            },
        )
