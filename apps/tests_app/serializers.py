from rest_framework import serializers

from .models import *


class TestAboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ["id", "is_active"]


class TestStartSerializer(serializers.ModelSerializer):
    tests = TestAboutSerializer(many=True, read_only=True)

    class Meta:
        model = TestStart
        fields = ["description", "tests"]


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
