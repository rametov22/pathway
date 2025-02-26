from django.urls import path
from .views import *


urlpatterns = [
    path("all/", NewsAllView.as_view(), name="all_news"),
    path("home/", NewsHomeView.as_view(), name="home_news"),
    path("detail/<int:id>/", NewsDetailView.as_view(), name="detail_news"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/<int:id>/read/",
        MarkGeneralNotificationsAsReadView.as_view(),
        name="mark-general-notification-read",
    ),
    path(
        "user/notifications/detail/<int:id>/",
        UserNotificationDetailView.as_view(),
        name="user-notifications-detail",
    ),
    path(
        "user/notifications/",
        UserNotificationListView.as_view(),
        name="user-notifications",
    ),
    path(
        "user/notifications/<int:id>/read/",
        MarkUserNotificationAsReadView.as_view(),
        name="mark-user-notification-read",
    ),
]
