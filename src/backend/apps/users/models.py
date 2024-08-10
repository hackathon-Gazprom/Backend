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
    IMAGE_ALLOWED_EXTENSIONS,
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
    middle_name = models.CharField("Отчество", max_length=150, blank=True)
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
        default=3,
        validators=[
            MinValueValidator(MIN_TIMEZONE),
            MaxValueValidator(MAX_TIMEZONE),
        ],
    )
    position = models.CharField(
        "Должность", max_length=255, null=True, blank=True
    )
    telegram = models.CharField(
        "Telegram", max_length=255, blank=True, null=True
    )
    city = models.CharField("Город", max_length=25, blank=True)
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
