from django.urls import path
from django.views.generic import TemplateView

from .views import FAQView, OurNetworksView, OurNetworksHomeView

urlpatterns = [
    path("our_networks_home/", OurNetworksHomeView.as_view(), name="oru_networks_home"),
    path("our_networks/", OurNetworksView.as_view(), name="our-networks"),
    path("FAQ/", FAQView.as_view(), name="FAQ"),
]
