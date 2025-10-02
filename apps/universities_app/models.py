from datetime import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Universities(models.Model):
    university_img = models.ImageField(upload_to="university/")
    university_name = models.CharField(
        max_length=256, verbose_name="Название университета"
    )
    website_link = models.URLField(null=True, blank=True)
    is_state = models.BooleanField(
        default=True, verbose_name="Государственный университет"
    )
    university_directions = models.ManyToManyField(
        "Directions",
        related_name="universities",
        verbose_name="Напраления университета",
    )
    country = models.ForeignKey(
        "Country",
        on_delete=models.PROTECT,
        related_name="universities",
        verbose_name="Страна",
    )
    city = models.CharField(max_length=256, verbose_name="Город")
    year_of_study = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name="Год обучения"
    )
    year_founded = models.IntegerField(
        validators=[MaxValueValidator(datetime.now().year)],
        verbose_name="Год основания",
    )
    students_count = models.IntegerField(verbose_name="Количество студентов")
    international_students_count = models.IntegerField(
        verbose_name="Количество иностранных студентов"
    )
    acceptance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Процент зачисления",
    )
    rating_qs = models.IntegerField()
    rating_the = models.IntegerField()
    rating_us_news = models.IntegerField(default=999)
    history_university = models.TextField(verbose_name="История университета")
    school_categories = models.ManyToManyField("SchoolCategory", blank=True)

    def __str__(self):
        return f"{self.university_name}"


class SchoolCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    country_img = models.ImageField(upload_to="country/")
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256, null=True, blank=True)
    about_universities = models.TextField()
    advantages_universities = models.TextField()
    manual_order = models.PositiveIntegerField(
        default=0, verbose_name="Позиция в списке"
    )

    gdp = models.BigIntegerField()
    edu_quality_rank = models.IntegerField()
    universities_count = models.IntegerField()
    average_expenses = models.IntegerField()
    universities_top300_count = models.IntegerField()

    def __str__(self):
        return self.name


class Directions(models.Model):
    direction = models.CharField(max_length=256, verbose_name="Направления")

    def __str__(self):
        return self.direction
