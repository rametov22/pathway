from django.db.models.functions import Coalesce
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, viewsets

from .models import Universities, Country
from .serializers import (
    CountryDetailSerializer,
    CountrySerializer,
    UniversitiesDetailSerializer,
    UniversitiesSerializer,
)
from .filters import UniversityFilter


# UNIVERSITIES
class UniversitiesListView(generics.ListAPIView):
    serializer_class = UniversitiesSerializer

    def get_queryset(self):
        query = self.request.GET.get("search", "").strip()

        queryset = (
            Universities.objects.annotate(
                ranking_qs=Coalesce(F("rating_qs"), 9999),
                ranking_the=Coalesce(F("rating_the"), 9999),
            )
            .order_by("rating_qs", "rating_the")
            .select_related("country")
        )

        if query:
            queryset = queryset.filter(university_name__icontains=query)

        return queryset


class UniversitiesHomeView(generics.ListAPIView):
    serializer_class = UniversitiesSerializer

    def get_queryset(self):
        queryset = (
            Universities.objects.annotate(
                ranking_qs=Coalesce(F("rating_qs"), 9999),
                ranking_the=Coalesce(F("rating_the"), 9999),
            )
            .order_by("rating_qs", "rating_the")
            .select_related("country")[:4]
        )
        return queryset


class UniversitiesDetailView(generics.RetrieveAPIView):
    serializer_class = UniversitiesDetailSerializer

    def get_object(self):
        return get_object_or_404(Universities, id=self.kwargs["id"])


class UniversitiesSearchView(viewsets.ReadOnlyModelViewSet):
    queryset = Universities.objects.select_related("country")
    serializer_class = UniversitiesSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UniversityFilter
    search_fields = ["university_name", "country__name_ru", "country__name_en"]


# COUNTRIES
class CountryListView(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        query = self.request.GET.get("search", "").strip()

        queryset = Country.objects.annotate(
            universities_count=Count("universities")
        ).order_by("-universities_count")

        if query:
            queryset = queryset.filter(
                Q(name_ru__icontains=query) | Q(name_en__icontains=query)
            )

        return queryset


class CountryHomeView(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.annotate(
            universities_count=Count("universities")
        ).order_by("-universities_count")[:4]
        return queryset


class CountryDetailView(generics.RetrieveAPIView):
    serializer_class = CountryDetailSerializer

    def get_object(self):
        return get_object_or_404(Country, id=self.kwargs["id"])
