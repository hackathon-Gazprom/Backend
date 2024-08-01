from itertools import groupby

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from api.fields import Base64ImageField
from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Employee, Project
from .constants import SUBORDINATES

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения информации о работнике в дереве."""

    image = Base64ImageField(source="user.image")

    class Meta:
        model = Employee
        fields = ("id", "user_id", "image")


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания проекта."""

    owner = serializers.CharField(read_only=True)
    status = serializers.ChoiceField(
        choices=Project.Status.choices, default=Project.Status.NOT_STARTED
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "owner",
            "status",
            "description",
            "started",
            "ended",
        )

    def validate(self, attrs):
        errors = {}
        if attrs["started"] > attrs["ended"]:
            errors["started"] = GREATER_THAN_ENDED_DATE
        if timezone.now().date() > attrs["started"]:
            errors["started"] = LESS_THAN_TODAY
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def to_representation(self, instance):
        """Отображение статуса в читабельный вид."""
        data = super().to_representation(instance)
        data["status"] = instance.get_status_display()
        return data


class ProjectGetSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()
    status = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "owner",
            "status",
            "employees",
            "description",
            "started",
            "ended",
        )
        read_only_fields = fields

    def get_status(self, obj):
        return obj.get_status_display()


class ProjectListSerializer(ProjectGetSerializer):
    """Сериалайзер для детального отображения информации."""

    def get_employees(self, obj):
        return Employee.objects.filter(
            project=obj, user__is_active=True
        ).count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения списка."""

    def get_employees(self, obj):
        supervisor = Employee.objects.get(project=obj, user=obj.owner)
        children = (
            Employee.objects.filter(project=obj, user__is_active=True)
            .exclude(id=supervisor.id)
            .select_related("user__profile")
        ).only(
            "id",
            "user_id",
            "user__image",
        )

        data = {
            i: list(g) for i, g in groupby(children, lambda c: c.parent_id)
        }
        res = EmployeeSerializer(supervisor).data
        res[SUBORDINATES] = []
        max_deep = 6

        def tree(parent_id, childs, deep=0):
            if deep >= max_deep:
                return
            if parent_id in data:
                for child in data[parent_id]:
                    child_data = EmployeeSerializer(child).data
                    childs.append(child_data)
                    child_data[SUBORDINATES] = []
                    tree(
                        child.user_id,
                        child_data[SUBORDINATES],
                        deep + 1,
                    )

        tree(obj.owner.id, res[SUBORDINATES])

        return res


class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "status")
