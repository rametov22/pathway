from rest_framework import serializers

from .models import *


class TestAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestAnswer
        fields = ["id", "answer", "is_correct"]


class TestQuestionSerializer(serializers.ModelSerializer):
    answers = TestAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = TestQuestion
        fields = ["id", "question", "answers"]


class TestSerializer(serializers.ModelSerializer):
    questions = TestQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ["id", "title", "questions"]
