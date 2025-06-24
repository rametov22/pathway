from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import generics, filters, viewsets, views, status

from .models import Directions, Universities, Country
from .serializers import (
    CountryDetailSerializer,
    CountrySerializer,
    UniversitiesDetailSerializer,
    UniversitiesSerializer,
)
from .filters import UniversityFilter


# UNIVERSITIES
class UniversitiesListView(views.APIView):

    def post(self, request: Request, *args, **kwargs):
        country_id = request.data.get("country_id", None)
        search_query = request.query_params.get("search", "").strip()

        queryset = (
            Universities.objects.annotate(
                ranking_qs=Coalesce(F("rating_qs"), 9999),
                ranking_the=Coalesce(F("rating_the"), 9999),
            )
            .order_by("rating_qs", "rating_the")
            .select_related("country")
        )
        # queryset = Universities.objects.select_related("country").order_by(
        #     "university_name"
        # )

        if country_id:
            queryset = queryset.filter(country_id=country_id)
        if search_query:
            queryset = queryset.filter(university_name__icontains=search_query)

        serializer = UniversitiesSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    search_fields = ["university_name", "country__name", "country__short_name"]


# COUNTRIES
class CountryListView(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        query = self.request.GET.get("search", "").strip()

        queryset = Country.objects.annotate(
            universities_count=Count("universities")
        ).order_by("name")

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(short_name__icontains=query)
            )

        return queryset


class CountryHomeView(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.annotate(
            universities_count=Count("universities")
        ).order_by("name")[:4]
        return queryset
        # -universities_count


class CountryDetailView(generics.RetrieveAPIView):
    serializer_class = CountryDetailSerializer

    def get_object(self):
        return get_object_or_404(Country, id=self.kwargs["id"])

    def get_serializer_context(self):
        return {"request": self.request}


class StaticFilter(views.APIView):
    def get(self, request, *args, **kwargs):
        filters = {
            "year_of_study": [
                {"value": 2, "label": _("2 года")},
                {"value": 4, "label": _("4 года")},
            ],
            "is_state": [
                {"value": "", "label": _("Все университеты")},
                {"value": True, "label": _("Государственный университет")},
                {"value": False, "label": _("Частный университет")},
            ],
            "direction": [
                {"value": direction.id, "label": direction.direction}
                for direction in Directions.objects.all()
            ],
        }
        return Response(filters, status=status.HTTP_200_OK)
