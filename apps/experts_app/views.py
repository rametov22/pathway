from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics

from .serializers import (
    ExpertsDetailSerializer,
    ExpertsSerializer,
    SuccessStoriesSerializer,
    SuccessStoriesDetailSerializer,
)
from .models import Expert, SuccessStories


class ExpertListView(generics.ListAPIView):
    serializer_class = ExpertsSerializer

    def get_queryset(self):
        query = self.request.GET.get("search", "").strip()

        queryset = Expert.objects.all().order_by("name")

        if query:
            queryset = queryset.filter(name__icontains=query)

        return queryset


class ExpertHomeView(generics.ListAPIView):
    serializer_class = ExpertsSerializer

    def get_queryset(self):
        queryset = Expert.objects.all().order_by("name")[:6]
        return queryset


class ExpertDetailView(generics.RetrieveAPIView):
    serializer_class = ExpertsDetailSerializer

    def get_object(self):
        return get_object_or_404(Expert, id=self.kwargs["id"])


class SuccessStoriesView(generics.ListAPIView):
    serializer_class = SuccessStoriesSerializer

    def get_queryset(self):
        return SuccessStories.objects.select_related("university").all()


class SuccessStoriesDetailView(generics.RetrieveAPIView):
    serializer_class = SuccessStoriesDetailSerializer

    def get_object(self):
        return get_object_or_404(SuccessStories, id=self.kwargs["id"])
