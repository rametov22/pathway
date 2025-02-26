from django.contrib import admin

from .models import FAQModel, OurNetworks


@admin.register(OurNetworks)
class OurNetworksAdmin(admin.ModelAdmin):
    pass


@admin.register(FAQModel)
class FAQAdmin(admin.ModelAdmin):
    pass
