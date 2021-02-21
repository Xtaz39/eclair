from __future__ import annotations

import re

from django.core.exceptions import ValidationError


# phone format that sberbank accepts
_phone_regexp = re.compile(r"^((\+7|7|8)?([0-9]){10})$")


def is_phone(value: str):
    if not _phone_regexp.match(value):
        raise ValidationError("Неверный формат номера телефона")


def is_coordinates(value: str):
    long, lat = value.replace(" ", "").split(",", maxsplit=1)
    try:
        float(long)
        float(lat)
    except ValueError:
        raise ValidationError("Введите широту и долготу через запятую")
