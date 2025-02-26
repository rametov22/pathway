from rest_framework import serializers

from .models import FAQModel, OurNetworks


class OurNetworksSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = OurNetworks
        fields = ["name", "url", "icon"]

    def get_icon(self, obj):
        if obj.icon:
            request = self.context.get("request")
            base_url = request.build_absolute_uri("/")[:-1]
            return f"{base_url}{obj.icon.url}"
        return None


class FAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQModel
        fields = "__all__"
