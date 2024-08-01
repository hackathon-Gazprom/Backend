from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.general.models import CreatedField
from .constants import GREATER_THAN_ENDED_DATE, STATUS_DISPLAY

User = get_user_model()


class Project(CreatedField):
    class Status(models.IntegerChoices):
        NOT_STARTED = 1, "Не начат"
        STARTED = 2, "Начат"
        ENDED = 3, "Закончен"

    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Руководитель проекта",
        related_name="projects",
    )
    status = models.IntegerField(
        choices=Status.choices, default=Status.NOT_STARTED
    )
    started = models.DateField("Начало")
    ended = models.DateField("Конец")

    class Meta:
        indexes = [
            models.Index(fields=("-created",), name="created_index"),
        ]
        ordering = ("-created",)
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.started > self.ended:
            raise ValidationError(GREATER_THAN_ENDED_DATE)
        super().save(*args, **kwargs)

    def get_status_display(self):
        return STATUS_DISPLAY.get(self.status, "Неизвестный статус")


class Employee(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"], name="unique_employee"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("parent")), name="unique_parent"
            ),
        ]
        default_related_name = "employers"
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{str(self.user)!r} на проекте {str(self.project)!r}"
