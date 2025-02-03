from django.shortcuts import get_object_or_404
from rest_framework import generics

from .serializers import ExpertsDetailSerializer, ExpertsSerializer
from .models import Expert


class ExpertListView(generics.ListAPIView):
    serializer_class = ExpertsSerializer

    def get_queryset(self):
        queryset = Expert.objects.all()
        return queryset


class ExpertHomeView(generics.ListAPIView):
    serializer_class = ExpertsSerializer

    def get_queryset(self):
        queryset = Expert.objects.all()[:6]
        return queryset


class ExpertDetailView(generics.RetrieveAPIView):
    serializer_class = ExpertsDetailSerializer

    def get_object(self):
        return get_object_or_404(Expert, id=self.kwargs["id"])
