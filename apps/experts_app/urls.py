from django.urls import path

from .views import (
    ExpertListView,
    ExpertHomeView,
    ExpertDetailView,
    SuccessStoriesDetailView,
    SuccessStoriesView,
)


urlpatterns = [
    path("all/", ExpertListView.as_view(), name="all_experts"),
    path("home/", ExpertHomeView.as_view(), name="home_experts"),
    path("detail/<int:id>/", ExpertDetailView.as_view(), name="detail_experts"),
    path("success/home/", SuccessStoriesView.as_view(), name="success_stories"),
    path(
        "success/detail/<int:id>/",
        SuccessStoriesDetailView.as_view(),
        name="success_stories_detail",
    ),
]
