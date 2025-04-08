import django_filters
from .models import Directions, Universities


class UniversityFilter(django_filters.FilterSet):
    year_of_study = django_filters.MultipleChoiceFilter(
        field_name="year_of_study",
        choices=[(2, "2 года"), (4, "4 года")],
        label="Год обучения",
    )
    is_state = django_filters.ChoiceFilter(
        field_name="is_state",
        choices=[
            ("", "Все университеты"),
            (True, "Государственный университет"),
            (False, "Частный университет"),
        ],
        label="Государственный университет",
        empty_label=None,
    )
    direction = django_filters.ModelMultipleChoiceFilter(
        queryset=Directions.objects.all(),
        field_name="university_directions",
        to_field_name="id",
        label="Направление",
    )

    class Meta:
        model = Universities
        fields = ["year_of_study", "is_state", "direction"]
