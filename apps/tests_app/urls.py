from django.urls import path
from .views import *


urlpatterns = [
    path("<int:pk>/", TestDetailView.as_view(), name="test-detail"),
    path("<int:test_id>/submit/", SubmitTestView.as_view(), name="submit-test"),
]
