from django.urls import path
from .views import *


urlpatterns = [
    path("register/user/", UserRegistrationView.as_view(), name="register"),
    path(
        "register/complete/<int:user_id>",
        CompleteRegistrationView.as_view(),
        name="register_complete",
    ),
    path(
        "register/options/", RegistrationOptionsView.as_view(), name="register_options"
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("auth/google/", GoogleLoginApiView.as_view(), name="google_auth"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
]
