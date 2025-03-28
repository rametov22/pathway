from django.shortcuts import render
from rest_framework import views, generics
from rest_framework.response import Response

from .models import FAQModel, OurNetworks
from .serializers import FAQSerializer, OurNetworksSerializer


class OurNetworksView(views.APIView):
    def get(self, request):
        networks = OurNetworks.objects.all()
        serializer = OurNetworksSerializer(
            networks, many=True, context={"request": request}
        )
        return Response(serializer.data)


class OurNetworksHomeView(views.APIView):
    def get(self, request):
        networks = OurNetworks.objects.filter(name__icontains="telegram")
        serializer = OurNetworksSerializer(
            networks, many=True, context={"request": request}
        )
        return Response(serializer.data)


class FAQView(generics.ListAPIView):
    serializer_class = FAQSerializer

    def get_queryset(self):
        return FAQModel.objects.all()
