from django.urls import include, path

from dashboard.views import (
    PortfolioCreateView,
    PortfolioDeleteView,
    PortfolioDetailView,
    PortfolioListView,
    ShareCreateView,
    ShareDeleteView,
    ShareDetailView,
    ShareListView,
    ShareUpdateView,
)

app_name = "dashboard"

urlpatterns = [
    path("", ShareListView.as_view(), name="index"),
    path("<int:pk>/", ShareDetailView.as_view(), name="detail"),
    path("create/", ShareCreateView.as_view(), name="create"),
    path("update/<int:pk>/", ShareUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", ShareDeleteView.as_view(), name="delete"),
    # Virtual portfolio
    path("portfolios/", PortfolioListView.as_view(), name="portfolio_list"),
    path("portfolios/create/", PortfolioCreateView.as_view(), name="portfolio_create"),
    path("portfolios/<int:pk>/", PortfolioDetailView.as_view(), name="portfolio_detail"),
    path("portfolios/<int:pk>/delete/", PortfolioDeleteView.as_view(), name="portfolio_delete"),
    path("api/", include("dashboard.api.urls")),
]
