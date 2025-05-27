import re


def validate_phone_number(phone_number: str) -> bool:
    pattern = re.compile(r"^\d{10}$")
    return bool(pattern.match(phone_number))
