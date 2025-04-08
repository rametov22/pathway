from django.utils.translation import gettext as _
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *


class TestStartView(APIView):
    def get(self, request):
        test_start = TestStart.objects.first()
        tests = Test.objects.all()

        if not test_start:
            return Response({"error": "No TestStart objects found"}, status=404)

        test_start_data = TestStartSerializer(test_start).data
        test_start_data["tests"] = TestAboutSerializer(tests, many=True).data
        return Response(test_start_data)


class TestDetailView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class SubmitTestView(APIView):
    def post(self, request, test_id):
        user = request.user
        test = Test.objects.get(id=test_id)
        user_answers = request.data.get("answers", {})

        correct_count = 0
        total_questions = test.questions.count()

        for question in test.questions.all():
            correct_answers = list(
                TestAnswer.objects.filter(
                    question=question, is_correct=True
                ).values_list("id", flat=True)
            )
            user_selected = user_answers.get(str(question.id), [])

            if set(user_selected) == set(correct_answers):
                correct_count += 1

        score_percentage = (
            (correct_count / total_questions) * 100 if total_questions > 0 else 0
        )
        passed = score_percentage >= 50
        status = passed
        status_message = (
            _("Прекрасно! Вы успешно прошли тест.")
            if passed
            else _("Упс! Попробуйте ещё раз — у вас всё получится.")
        )

        result = TestResult.objects.create(
            user=user,
            test=test,
            correct_answers=correct_count,
            total_questions=total_questions,
        )

        return Response(
            {
                "test": test.title,
                "correct_answers": correct_count,
                "total_questions": total_questions,
                "score": f"{total_questions}/{correct_count}",
                "status": status,
                "status_message": status_message,
            }
        )
