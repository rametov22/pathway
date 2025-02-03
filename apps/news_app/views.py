from django.shortcuts import get_object_or_404
from rest_framework import generics

from .models import News
from .serializers import NewsSerializer, NewsDetailSerializer


class NewsAllView(generics.ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        queryset = (
            News.objects.filter(show_news=True)
            .select_related("category")
            .order_by("-date_added")
        )
        return queryset


class NewsHomeView(generics.ListAPIView):
    serializer_class = NewsSerializer

    def get_queryset(self):
        queryset = (
            News.objects.filter(show_news=True)
            .select_related("category")
            .order_by("-date_added")[:4]
        )
        return queryset


class NewsDetailView(generics.RetrieveAPIView):
    serializer_class = NewsDetailSerializer

    def get_object(self):
        return get_object_or_404(News, id=self.kwargs["id"])
