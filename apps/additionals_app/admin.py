from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import FAQModel, OurNetworks


@admin.register(OurNetworks)
class OurNetworksAdmin(admin.ModelAdmin):
    pass


@admin.register(FAQModel)
class FAQAdmin(TabbedTranslationAdmin):
    pass
