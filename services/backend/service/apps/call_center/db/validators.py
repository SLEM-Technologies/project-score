from django.core import validators
from django.utils.regex_helper import _lazy_re_compile


def validate_is_digit(value: str) -> None:
    return validators.RegexValidator(
        _lazy_re_compile(r'^\d+\Z'),
        message='Ensure this value consists of digits.',
        code='invalid',
    )(value)
