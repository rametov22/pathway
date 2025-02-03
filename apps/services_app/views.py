from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions

from .models import *
from .serializers import (
    ConsultationRequestSerializer,
    ServiceSerializer,
    ServiceDetailSerializer,
)


class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        queryset = Service.objects.all().order_by("-created_at")
        return queryset


class ServiceHomeView(generics.ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        queryset = Service.objects.all().order_by("-created_at")[:4]
        return queryset


class ServiceDetailView(generics.RetrieveAPIView):
    serializer_class = ServiceDetailSerializer

    def get_object(self):
        return get_object_or_404(Service, id=self.kwargs["id"])


class ConsultationRequestCreateView(generics.CreateAPIView):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
