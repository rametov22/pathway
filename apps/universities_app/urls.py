from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CountryDetailView,
    CountryHomeView,
    CountryListView,
    StaticFilter,
    UniversitiesDetailView,
    UniversitiesHomeView,
    UniversitiesListView,
    UniversitiesSearchView,
)


router = DefaultRouter()
router.register(r"search", UniversitiesSearchView, basename="search")

urlpatterns = [
    path("all/", UniversitiesListView.as_view(), name="all_universities"),
    path("home/", UniversitiesHomeView.as_view(), name="home_universities"),
    path(
        "detail/<int:id>/", UniversitiesDetailView.as_view(), name="detail_universities"
    ),
    path("all_country/", CountryListView.as_view(), name="all_countries"),
    path("home_country/", CountryHomeView.as_view(), name="home_countries"),
    path(
        "detail_country/<int:id>/", CountryDetailView.as_view(), name="detail_countries"
    ),
    path("static-filters/", StaticFilter.as_view(), name="static-filters"),
]

urlpatterns += router.urls
