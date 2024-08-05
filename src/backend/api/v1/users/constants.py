from apps.users.constants import MAX_PHONE_LENGTH, MAX_TIMEZONE, MIN_TIMEZONE

TELEGRAM_PATTERN = r"^@[a-zA-Z0-9\\._]+$"

ERROR_TIMEZONE = (
    f"Тайм зона может быть только в пределах "
    f"от {MIN_TIMEZONE!r} до {MAX_TIMEZONE!r}."
)
ERROR_TELEGRAM = (
    "Ник в телеграмме должен начинаться с `@` и содержать только "
    "латинские буквы, цифры, а также точку и нижнее подчеркивание."
)
ERROR_PHONE = (
    f"Номер должен начинаться с 8 и содержать {MAX_PHONE_LENGTH} цифр."
)
USERS_PAGE_SIZE = 24
