from django.conf import settings
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests

from .models import User
from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegistrationOptionsSerializer,
    UserRegistrationSerializer,
    CompleteRegistrationSerializer,
    ProfileUpdateSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response(
                {"message": "Пользователь создан.", **data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteRegistrationView(generics.UpdateAPIView):
    serializer_class = CompleteRegistrationSerializer
    lookup_url_kwarg = "user_id"

    def get_queryset(self):
        return User.objects.all()

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            user, tokens = serializer.save()
            return Response(
                {
                    "message": "Профиль обновлен, пользователь активирован",
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                }
            )
        return Response(serializer.errors, status=400)


class RegistrationOptionsView(views.APIView):

    def get(self, request):
        serializer = RegistrationOptionsSerializer({}, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class GoogleLoginApiView(views.APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )

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
                {"message": "Профиль успещно обновлен", "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
