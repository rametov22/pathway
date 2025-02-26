from django.urls import path
from .views import *


urlpatterns = [
    path("test_start/", TestStartView.as_view(), name="test_start"),
    path("<int:pk>/", TestDetailView.as_view(), name="test-detail"),
    path("<int:test_id>/submit/", SubmitTestView.as_view(), name="submit-test"),
]
