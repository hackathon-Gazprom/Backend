from django.contrib.auth import get_user_model
from django.db import models

from apps.general.models import CreatedField
from .constants import STATUS_DISPLAY

User = get_user_model()


class Team(models.Model):
    name = models.CharField("Название", max_length=150, db_index=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор"
    )
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"
        ordering = ("name",)
        default_related_name = "teams"

    def __str__(self):
        return self.name


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
    teams = models.ManyToManyField(
        Team, related_name="projects", through="ProjectTeam"
    )
    started = models.DateField("Начало")
    ended = models.DateField("Конец")

    class Meta:
        indexes = [
            models.Index(fields=("-created",), name="created_index"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(started__lte=models.F("ended")),
                name="started_index",
            )
        ]
        ordering = ("-created",)
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def get_status_display(self):
        return STATUS_DISPLAY.get(self.status, "Неизвестный статус")


class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "project_team"
        verbose_name = "Проект-команда"
        verbose_name_plural = "Проекты-команды"

    def __str__(self):
        return f"{self.project} - {self.team}"


class Department(models.Model):
    name = models.CharField("Отдел", max_length=150, unique=True)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self):
        return self.name


class Member(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, verbose_name="Команда"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Участник"
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name="Отдел"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name="Руководитель",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user"], name="unique_member"
            ),
        ]
        default_related_name = "members"
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self):
        return self.user.full_name()
