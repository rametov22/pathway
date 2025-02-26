from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size_mb = 2
    max_size_bytes = max_size_mb * 1024 * 1024

    if value.size > max_size_bytes:
        raise ValidationError(f"Файл слишком большой!")
