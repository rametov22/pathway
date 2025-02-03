from rest_framework import serializers

from .models import Expert


class ExpertsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expert
        fields = (
            "id",
            "img",
            "name",
            "job",
        )


class ExpertsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expert
        fields = (
            "img",
            "name",
            "job",
            "phone_number",
            "expert_about",
        )
