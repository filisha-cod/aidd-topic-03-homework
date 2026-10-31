"""
Views — Agent B style: explicit, LoginRequiredMixin, portfolio feature.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import PortfolioForm, ShareModelForm, TradeForm
from .models import Portfolio, PortfolioTransaction, Share
from .services.graph import get_graph
from .services.portfolio import PortfolioError, execute_buy, execute_sell


class ShareListView(ListView):
    model = Share
    template_name = "dashboard/list.html"
    paginate_by = 50
    context_object_name = "share_list"
    ordering = ["name"]


class ShareDetailView(View):
    def get(self, request, pk):
        share = get_object_or_404(Share, pk=pk)
        days = int(request.GET.get("days", 180))
        days = max(7, min(days, 730))
        return render(
            request,
            "dashboard/detail.html",
            {"share": share, "plot_div": get_graph(share, days=days), "days": days},
        )


class ShareCreateView(LoginRequiredMixin, CreateView):
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")
    login_url = reverse_lazy("user:auth")


class ShareUpdateView(LoginRequiredMixin, UpdateView):
    model = Share
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")
    login_url = reverse_lazy("user:auth")


class ShareDeleteView(LoginRequiredMixin, DeleteView):
    model = Share
    template_name = "dashboard/delete.html"
    success_url = reverse_lazy("dashboard:index")
    login_url = reverse_lazy("user:auth")


# ----- Portfolio feature (Agent B new functionality) -----

class PortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = "dashboard/portfolio_list.html"
    context_object_name = "portfolios"
    login_url = reverse_lazy("user:auth")

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "dashboard/portfolio_form.html"
    success_url = reverse_lazy("dashboard:portfolio_list")
    login_url = reverse_lazy("user:auth")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Portfolio created")
        return super().form_valid(form)


class PortfolioDetailView(LoginRequiredMixin, View):
    login_url = reverse_lazy("user:auth")

    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = TradeForm()
        return render(
            request,
            "dashboard/portfolio_detail.html",
            {
                "portfolio": portfolio,
                "items": portfolio.items.select_related("share").all(),
                "transactions": portfolio.transactions.select_related("share")[:50],
                "form": form,
                "cost_basis": portfolio.total_cost_basis(),
                "market_value": portfolio.total_market_value(),
                "pnl": portfolio.total_pnl(),
                "pnl_pct": portfolio.total_pnl_percent(),
            },
        )

    def post(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        form = TradeForm(request.POST)
        if form.is_valid():
            share = form.cleaned_data["share"]
            side = form.cleaned_data["side"]
            qty = form.cleaned_data["quantity"]
            price = form.cleaned_data["price"]
            note = form.cleaned_data.get("note") or ""
            try:
                if side == PortfolioTransaction.BUY:
                    execute_buy(portfolio, share, qty, price, note)
                    messages.success(request, f"Bought {qty} {share.ticker}")
                else:
                    execute_sell(portfolio, share, qty, price, note)
                    messages.success(request, f"Sold {qty} {share.ticker}")
            except PortfolioError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Invalid trade form")
        return redirect("dashboard:portfolio_detail", pk=pk)


class PortfolioDeleteView(LoginRequiredMixin, DeleteView):
    model = Portfolio
    template_name = "dashboard/portfolio_confirm_delete.html"
    success_url = reverse_lazy("dashboard:portfolio_list")
    login_url = reverse_lazy("user:auth")

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)
