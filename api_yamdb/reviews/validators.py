from datetime import datetime

from rest_framework.exceptions import ValidationError


def validate_year(year):
    if year > datetime.now().year:
        raise ValidationError("Год не может быть больше текущего года")
    if year < 0:
        raise ValidationError("Год не может быть меньше 0")
