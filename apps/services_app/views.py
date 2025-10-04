from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import *
from .serializers import (
    ConsultationRequestSerializer,
    ServiceSerializer,
    ServiceDetailSerializer,
    DayOfWeeksSerializer,
    ConsultationServicesSerializer,
    EducationLevelsSerializer,
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

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_object(self):
        return get_object_or_404(Service, id=self.kwargs["id"])

    def post(self, request, *args, **kwargs):
        service = self.get_object()
        existing_application = ServiceApplication.objects.filter(
            user=request.user, service=service
        ).first()

        if existing_application:
            return Response(
                {
                    "message": _(
                        "Вы уже оставили заявку на этот сервис. Повторная отправка невозможна."
                    ),
                    "status": existing_application.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application = ServiceApplication.objects.create(
            user=request.user, service=service
        )
        return Response(
            {"message": _("Заявка успещно отправлена"), "status": application.status},
            status=status.HTTP_201_CREATED,
        )


class ConsultationRequestCreateView(generics.CreateAPIView):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class DayOfWeeksListAPIView(generics.ListAPIView):
    queryset = DayOfWeeks.objects.all()
    serializer_class = DayOfWeeksSerializer


class ConsultationServicesListAPIView(generics.ListAPIView):
    queryset = ConsultationServices.objects.all()
    serializer_class = ConsultationServicesSerializer


class EducationLevelsListAPIView(generics.ListAPIView):
    queryset = EducationLevels.objects.all()
    serializer_class = EducationLevelsSerializer
