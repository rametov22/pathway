from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, permissions, status

from .models import News, Notification, UserNotification, UserNotificationReadStatus
from .serializers import (
    NewsSerializer,
    NewsDetailSerializer,
    NotificationSerializer,
    UserNotificationDetailSerializer,
    UserNotificationSerializer,
)


class NewsAllView(generics.ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        queryset = (
            News.objects.filter(show_news=True)
            .select_related("category")
            .order_by("-date_added")
        )
        return queryset


class NewsHomeView(generics.ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        queryset = (
            News.objects.filter(show_news=True)
            .select_related("category")
            .order_by("-date_added")[:4]
        )
        return queryset


class NewsDetailView(generics.RetrieveAPIView):
    serializer_class = NewsDetailSerializer

    def get_object(self):
        return get_object_or_404(News, id=self.kwargs["id"])


class NotificationListView(generics.ListAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Notification.objects.all().order_by("-created_at")


class UserNotificationListView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


class UserNotificationDetailView(generics.RetrieveAPIView):
    serializer_class = UserNotificationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(UserNotification, id=self.kwargs["id"])


class MarkGeneralNotificationsAsReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        notification = get_object_or_404(Notification, id=self.kwargs["id"])

        obj, created = UserNotificationReadStatus.objects.get_or_create(
            user=request.user, notification=notification
        )
        obj.is_read = True
        obj.save()

        return Response(
            {"message": "Общее уведомление помечено как прочитанное"},
            status=status.HTTP_200_OK,
        )


class MarkUserNotificationAsReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return None
        return super().get_serializer_class()

    def patch(self, request, *args, **kwargs):
        notification = get_object_or_404(
            UserNotification, id=self.kwargs["id"], user=request.user
        )
        notification.is_read = True
        notification.save()
        return Response(
            {"message": "Личное уведомление помечено как прочитанное"},
            status=status.HTTP_200_OK,
        )
