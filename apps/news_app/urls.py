from django.urls import path
from .views import *


urlpatterns = [
    path("all/", NewsAllView.as_view(), name="all_news"),
    path("home/", NewsHomeView.as_view(), name="home_news"),
    path("detail/<int:id>/", NewsDetailView.as_view(), name="detail_news"),
]
