from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django_cleanup.cleanup import cleanup_select

from .constants import (
    CITY_MAX_LENGTH,
    DEFAULT_TIME_ZONE,
    IMAGE_ALLOWED_EXTENSIONS,
    MAX_LENGTH,
    MAX_LENGTH_NAME,
    MAX_PHONE_LENGTH,
    MAX_TIMEZONE,
    MIN_TIMEZONE,
    RE_PHONE,
)
from .managers import CustomUserManager


@cleanup_select
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None
    first_name = models.CharField(
        "Фамилия", max_length=MAX_LENGTH_NAME, blank=True, db_index=True
    )
    last_name = models.CharField(
        "Имя", max_length=MAX_LENGTH_NAME, blank=True, db_index=True
    )
    middle_name = models.CharField(
        "Отчество", max_length=MAX_LENGTH_NAME, blank=True, db_index=True
    )
    image = models.ImageField(
        upload_to="images/users/",
        validators=[FileExtensionValidator(IMAGE_ALLOWED_EXTENSIONS)],
        blank=True,
        verbose_name="Аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        abstract = False
        indexes = [
            models.Index(fields=["first_name", "last_name", "middle_name"])
        ]
        ordering = ["last_name", "first_name", "middle_name"]

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField("О себе", blank=True)
    birthday = models.DateField("День рождения", null=True, blank=True)
    time_zone = models.SmallIntegerField(
        "Часовой пояс",
        blank=True,
        default=DEFAULT_TIME_ZONE,
        validators=[
            MinValueValidator(MIN_TIMEZONE),
            MaxValueValidator(MAX_TIMEZONE),
        ],
    )
    position = models.CharField(
        "Должность",
        max_length=MAX_LENGTH,
        null=True,
        blank=True,
        db_index=True,
    )
    telegram = models.CharField(
        "Telegram", max_length=MAX_LENGTH, blank=True, null=True
    )
    city = models.CharField(
        "Город", max_length=CITY_MAX_LENGTH, blank=True, db_index=True
    )
    phone = models.CharField(
        "Телефон",
        max_length=MAX_PHONE_LENGTH,
        validators=[RegexValidator(RE_PHONE)],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.email
