from django.urls import path
from .views import *


urlpatterns = [
    path("register/user/", RegisterStep1View.as_view(), name="register_user"),
    path("register/verify/", VerifyCodeView.as_view(), name="register_verify"),
    path(
        "register/complete/<int:user_id>/",
        CompleteProfileView.as_view(),
        name="register_complete",
    ),
    path("questions/", QuestionListView.as_view(), name="questions"),
    path("register/answers/", UserAnswerView.as_view(), name="answers"),
    path("login/", LoginView.as_view(), name="login"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="forgot_password"),
    path(
        "password/verify_code/",
        VerifyResetCodeView.as_view(),
        name="password_code_verify",
    ),
    path("password/reset/", ResetPasswordView.as_view(), name="reset_password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("delete/account/", DeleteAccountView.as_view(), name="delete_account"),
    path("auth/google/", GoogleLoginApiView.as_view(), name="google_auth"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("countries/", CountryListView.as_view(), name="country_list"),
    path("home/progress/", HomeProgressView.as_view(), name="home_progress"),
    path(
        "profile/applications/",
        ProfileApplicationsView.as_view(),
        name="profile_applications",
    ),
    path(
        "profile/applications/all/",
        ProfileApplicationsAllView.as_view(),
        name="profile_applications_all",
    ),
    path(
        "profile/documents/", ProfileDocumentsView.as_view(), name="profile_documents"
    ),
    path(
        "profile/documents/all/",
        ProfileDocumentsAllView.as_view(),
        name="profile_documents_all",
    ),
    path(
        "profile/documents/delete/<int:pk>/",
        ProfileDocumentsAllView.as_view(),
        name="profile_documents_delete",
    ),
    path("profile/experts/", ProfileExpertsView.as_view(), name="profile_experts"),
    path("profile/progress/", ProfileProgressView.as_view(), name="profile_progress"),
    path(
        "profile/progress/detail/",
        ProfileProgressDetailView.as_view(),
        name="profile_progress_detail",
    ),
    path(
        "calendar/applications/",
        UserApplicationsListView.as_view(),
        name="applications",
    ),
    path(
        "user/documents/upload/",
        UserDocumentUploadView.as_view(),
        name="user_document_upload",
    ),
    path(
        "applications/documents/upload/",
        ApplicationDocumentUploadView.as_view(),
        name="application_document_upload",
    ),
]
