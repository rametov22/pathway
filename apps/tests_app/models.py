from django.db import models
from django.conf import settings


class Test(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class TestQuestion(models.Model):
    test = models.ForeignKey("Test", related_name="questions", on_delete=models.PROTECT)
    question = models.TextField()

    def __str__(self):
        return f"{self.question}"


class TestAnswer(models.Model):
    question = models.ForeignKey(
        "TestQuestion", related_name="answers", on_delete=models.PROTECT
    )
    answer = models.CharField(max_length=512)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.answer}"


class TestResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    correct_answers = models.IntegerField()
    total_questions = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"
