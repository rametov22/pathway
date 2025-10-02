from django.urls import path

from .views import *


urlpatterns = [
    path("all/", ServiceListView.as_view(), name="all_service"),
    path("home/", ServiceHomeView.as_view(), name="home_service"),
    path("detail/<int:id>/", ServiceDetailView.as_view(), name="detail_service"),
    path("consultation/", ConsultationRequestCreateView.as_view(), name="consultation"),
    path("day_weeks/", DayOfWeeksListAPIView.as_view(), name="day-weeks"),
    path("our_services/", ConsultationServicesListAPIView.as_view(), name="services"),
    path(
        "education_levels/",
        EducationLevelsListAPIView.as_view(),
        name="education-levels",
    ),
]
