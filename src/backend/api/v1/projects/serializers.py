from collections import defaultdict

from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from api.fields import Base64ImageField
from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Employee, Project
from .constants import MAX_DEEP_SUBORDINATES, SUBORDINATES, WITHOUT_PARENT

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения информации о работнике в дереве."""

    image = Base64ImageField(source="user.image")
    subordinates = serializers.ListField(read_only=True)
    without_parent = serializers.ListField(read_only=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "user_id",
            "position",
            "image",
            "subordinates",
            "without_parent",
        )


class ProjectSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания и обновления проекта."""

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

    def update(self, instance, validated_data):
        data = {
            "name": validated_data.get("name"),
            "description": validated_data.get("description"),
        }
        changed = False
        for key, value in data.items():
            if value is None:
                continue
            changed = True
            setattr(instance, key, value)

        if changed:
            instance.save()
        return instance


class ProjectBaseSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер проекта"""

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
        swagger_schema_fields = {"tags": ["project"]}

    def get_status(self, obj):
        return obj.get_status_display()


class ProjectListSerializer(ProjectBaseSerializer):
    """Сериалайзер для детального отображения информации."""

    def get_employees(self, obj) -> int:
        return Employee.objects.filter(
            project=obj, user__is_active=True
        ).count()


class ProjectDetailSerializer(ProjectBaseSerializer):
    """Сериалайзер для отображения списка."""

    @swagger_serializer_method(serializer_or_field=EmployeeSerializer)
    def get_employees(self, obj):
        request = self.context.get("request")
        max_deep = request.query_params.get("deep", f"{MAX_DEEP_SUBORDINATES}")
        try:
            max_deep = int(max_deep)
        except ValueError:
            max_deep = MAX_DEEP_SUBORDINATES
        else:
            max_deep = min(max(1, max_deep), MAX_DEEP_SUBORDINATES)

        supervisor = Employee.objects.get(project=obj, user=obj.owner)
        children = (
            Employee.objects.filter(project=obj, user__is_active=True)
            .exclude(id=supervisor.id)
            .select_related("user__profile")
        ).only(
            "id",
            "user_id",
            "position",
            "user__image",
        )
        return self.get_tree(children, supervisor, max_deep)

    def get_tree(self, children, supervisor, max_deep):
        tree = defaultdict(list)
        nodes = defaultdict(list)
        for child in children:
            nodes[child.parent_id].append(child)

        def build_subtree(employee, deep=0):
            subtree = EmployeeSerializer(employee).data
            subtree[SUBORDINATES] = []
            for child in nodes[employee.id]:
                if deep + 1 >= max_deep:
                    break
                subtree[SUBORDINATES].append(
                    build_subtree(child, deep=deep + 1)
                )
            return subtree

        for parent_id in (supervisor.id, None):  # owner and non parent
            [
                tree[parent_id].append(build_subtree(node, 0))
                for node in nodes[parent_id]
            ]
        res = EmployeeSerializer(supervisor).data
        res[SUBORDINATES] = tree[supervisor.id]
        res[WITHOUT_PARENT] = tree[None]
        return res


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Сериалайзер для смены статуса"""

    class Meta:
        model = Project
        fields = ("id", "status")
