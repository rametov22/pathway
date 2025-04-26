from collections import defaultdict
from datetime import datetime
from django.conf import settings
from django.db.models import F
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from django_countries import countries
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils import translation

from .models import User, UserApplication, UserDocument, ApplicationDocument
from .serializers import *
from .pagination import Limit10Pagination
from apps.experts_app.serializers import ExpertsSerializer
from apps.experts_app.models import Expert
from apps.services_app.models import ServiceApplication


class RegisterStep1View(generics.CreateAPIView):
    serializer_class = RegisterStep1Serializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user_id": user.id,
                "message": _("Код подтвержденя отправлен."),
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyCodeView(generics.CreateAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data, status=status.HTTP_200_OK)


class CompleteProfileView(generics.UpdateAPIView):
    serializer_class = CompleteProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return User.objects.get(id=self.kwargs["user_id"])

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"user_id": user.id, "message": _("Профиль успешно обновлён.")},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Question.objects.all()


class UserAnswerView(generics.CreateAPIView):
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        return Response(data, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class VerifyResetCodeView(generics.CreateAPIView):
    serializer_class = VerifyResetCodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": _("Successfully logged out.")}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message", _("Аккаунт успещно удалён")}, status=status.HTTP_204_NO_CONTENT
        )


class GoogleLoginApiView(views.APIView):
    def post(self, request):
        token = request.data.get("token")
        platform = request.data.get("platform")

        if not token:
            return Response({"error": "Token is required"}, status=400)

        if platform == "android":
            client_id = settings.GOOGLE_CLIENT_ID_ANDROID
        elif platform == "ios":
            client_id = settings.GOOGLE_CLIENT_ID_IOS
        else:
            return Response({"error": "Invalid platform specified"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

            if "email" not in idinfo:
                return Response({"error": "Invalid token"}, status=400)

            email = idinfo["email"]
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")
            picture = idinfo.get("picture", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name or email.split("@")[0],
                    "last_name": last_name,
                    "google_photo_url": picture,
                    "is_active": True,
                },
            )

            if not user.google_photo_url and picture:
                user.google_photo_url = picture
                user.save(update_fields=["google_photo_url"])

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=200,
            )

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=400)


# PROFILE
class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": _("Профиль успешно обновлён."), "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryListView(generics.ListAPIView):
    serializer_class = CountrySerializerAccounts
    permission_classes = [permissions.AllowAny]
    pagination_class = Limit10Pagination

    def get_queryset(self):
        country_list = [{"code": code, "name": name} for code, name in countries]
        return country_list


class ProfileApplicationsView(generics.ListAPIView):
    serializer_class = UserApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserApplication.objects.filter(
            user=self.request.user, status__in=["approved", "in_progress", "rejected"]
        )[:2]


class ProfileApplicationsAllView(generics.ListAPIView):
    serializer_class = UserApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserApplication.objects.filter(
            user=self.request.user, status__in=["approved", "in_progress", "rejected"]
        )


class ProfileDocumentsView(generics.ListAPIView):
    serializer_class = ProfileDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        user_documents = list(UserDocument.objects.filter(user=user))[:2]

        return user_documents


class ProfileDocumentsAllView(generics.ListAPIView):
    serializer_class = ProfileDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        user_documents = list(UserDocument.objects.filter(user=user))

        return user_documents

    def delete(self, request, *args, **kwargs):
        document_id = kwargs.get("pk")
        document = get_object_or_404(UserDocument, id=document_id, user=request.user)
        document.delete()
        return Response(
            {"message": _("Документ успешно удалён")}, status=status.HTTP_204_NO_CONTENT
        )


class HomeProgressView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        documents_submitted = UserApplication.objects.filter(
            user=user, status="approved"
        ).count()
        documents_left = UserApplication.objects.filter(
            user=user, status__in=["pending", "in_progress", "rejected"]
        ).count()

        total_applications = documents_submitted + documents_left
        progress_percentage = (
            (documents_submitted / total_applications * 100)
            if total_applications > 0
            else 0
        )

        applications_qs = (
            UserApplication.objects.filter(user=user).order_by("deadline_date")
        )[:2]
        applications = HomeProgressSerializer(
            applications_qs, many=True, context={"request": request}
        ).data

        return Response(
            {
                "documents_submitted": documents_submitted,
                "left": documents_left,
                "percentage": f"{round(progress_percentage)}%",
                "list_documents": applications,
            }
        )


class ProfileProgressView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        documents_submitted = UserApplication.objects.filter(
            user=user, status="approved"
        ).count()
        documents_left = UserApplication.objects.filter(
            user=user, status__in=["pending", "in_progress", "rejected"]
        ).count()

        total_applications = documents_submitted + documents_left
        progress_percentage = (
            (documents_submitted / total_applications * 100)
            if total_applications > 0
            else 0
        )

        return Response(
            {
                "documents_submitted": documents_submitted,
                "left": documents_left,
                "percentage": f"{round(progress_percentage)}%",
            }
        )


class ProfileProgressDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        documents_submitted = UserApplication.objects.filter(
            user=user, status="approved"
        ).count()
        documents_left = UserApplication.objects.filter(
            user=user, status__in=["pending", "in_progress", "rejected"]
        ).count()

        total_applications = documents_submitted + documents_left
        progress_percentage = (
            (documents_submitted / total_applications * 100)
            if total_applications > 0
            else 0
        )

        applications = (
            UserApplication.objects.filter(user=user)
            .annotate(default_application_title=F("default_application__title"))
            .values(
                "id",
                "default_application_title",
                "status",
                "deadline_date",
            )
            .order_by("deadline_date")
        )

        grouped_applications = defaultdict(list)
        for app in applications:
            date_str = (
                app["deadline_date"].strftime("%d %B %Y")
                if app["deadline_date"]
                else "Без даты"
            )
            grouped_applications[date_str].append(app)

        response_data = [
            {"date": date, "applications": apps}
            for date, apps in grouped_applications.items()
        ]

        return Response(
            {
                "documents_submitted": documents_submitted,
                "left": documents_left,
                "percentage": f"{round(progress_percentage)}%",
                "list_documents": response_data,
            }
        )


class ProfileExpertsView(generics.ListAPIView):
    serializer_class = ExpertsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        approved_services = ServiceApplication.objects.filter(
            user=user, status="approved"
        ).values_list("service", flat=True)
        return Expert.objects.filter(services__in=approved_services).distinct()


# DOCUMENTS
class UserApplicationsListView(generics.ListAPIView):
    serializer_class = UserApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        deadline_date = request.query_params.get("deadline_date")

        user_applications = UserApplication.objects.filter(user=user)

        if deadline_date:
            try:
                deadline_date = datetime.strptime(deadline_date, "%Y-%m-%d").date()
                user_applications = user_applications.filter(
                    deadline_date__date=deadline_date
                )
            except ValueError:
                return Response(
                    {"error": "Invalid date format. User YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user_applications = user_applications.order_by("deadline_date")

        grouped_applications = defaultdict(list)
        for app in user_applications:
            serializer = UserApplicationSerializer(app, context={"request": request})
            grouped_applications[app.deadline_date.strftime("%d %B %Y")].append(
                serializer.data
            )

        response_data = [
            {"date": date, "applications": apps}
            for date, apps in grouped_applications.items()
        ]

        return Response(response_data)


class ApplicationDocumentUploadView(generics.CreateAPIView):
    serializer_class = ApplicationDocumentUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserDocumentUploadView(generics.CreateAPIView):
    serializer_class = UserDocumentUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class DocumentDeleteView(generics.Dele):
