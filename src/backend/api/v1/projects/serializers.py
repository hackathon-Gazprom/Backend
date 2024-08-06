from collections import defaultdict

from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from api.fields import Base64ImageField
from api.v1.projects.constants import (
    SUBORDINATES,
    WITHOUT_PARENT,
    MAX_DEEP_SUBORDINATES,
)
from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Project, Team, Member

User = get_user_model()


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


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Сериалайзер для смены статуса"""

    status = serializers.ChoiceField(choices=Project.Status.choices)

    class Meta:
        model = Project
        fields = ("id", "status")


# class EmployeeSerializer(serializers.ModelSerializer):
#     """Сериалайзер для отображения информации о работнике в дереве."""
#
#     image = Base64ImageField(source="user.image")
#     subordinates = serializers.ListField(read_only=True)
#     without_parent = serializers.ListField(read_only=True)
#
#     class Meta:
#         model = Employee
#         fields = (
#             "id",
#             "user_id",
#             "image",
#             "subordinates",
#             "without_parent",
#         )


# class ProjectBaseSerializer(serializers.ModelSerializer):
#     """Базовый сериалайзер проекта"""
#
#     owner = serializers.CharField()
#     status = serializers.SerializerMethodField()
#     employees = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Project
#         fields = (
#             "id",
#             "name",
#             "owner",
#             "status",
#             "employees",
#             "description",
#             "started",
#             "ended",
#         )
#         read_only_fields = fields
#         swagger_schema_fields = {"tags": ["project"]}
#
#     def get_status(self, obj):
#         return obj.get_status_display()


# class ProjectListSerializer(ProjectBaseSerializer):
#     """Сериалайзер для детального отображения информации."""
#
#     def get_employees(self, obj) -> int:
#         return Employee.objects.filter(
#             project=obj, user__is_active=True
#         ).count()


# class ProjectDetailSerializer(ProjectBaseSerializer):
#     """Сериалайзер для отображения списка."""
#
#     @swagger_serializer_method(serializer_or_field=EmployeeSerializer)
#     def get_employees(self, obj):
#         request = self.context.get("request")
#         max_deep = request.query_params.get("deep", f"{MAX_DEEP_SUBORDINATES}")
#         try:
#             max_deep = int(max_deep)
#         except ValueError:
#             max_deep = MAX_DEEP_SUBORDINATES
#         else:
#             max_deep = min(max(1, max_deep), MAX_DEEP_SUBORDINATES)
#
#         supervisor = Employee.objects.get(project=obj, user=obj.owner)
#         children = (
#             Employee.objects.filter(project=obj, user__is_active=True)
#             .exclude(id=supervisor.id)
#             .select_related("user__profile")
#         ).only(
#             "id",
#             "user_id",
#             "user__image",
#         )
#         return self.get_tree(children, supervisor, max_deep)
#
#     def get_tree(self, children, supervisor, max_deep):
#         tree = defaultdict(list)
#         nodes = defaultdict(list)
#         for child in children:
#             nodes[child.parent_id].append(child)
#
#         def build_subtree(employee, deep=0):
#             subtree = EmployeeSerializer(employee).data
#             subtree[SUBORDINATES] = []
#             for child in nodes[employee.id]:
#                 if deep + 1 >= max_deep:
#                     break
#                 subtree[SUBORDINATES].append(
#                     build_subtree(child, deep=deep + 1)
#                 )
#             return subtree
#
#         for parent_id in (supervisor.id, None):  # owner and non parent
#             [
#                 tree[parent_id].append(build_subtree(node, 0))
#                 for node in nodes[parent_id]
#             ]
#         res = EmployeeSerializer(supervisor).data
#         res[SUBORDINATES] = tree[supervisor.id]
#         res[WITHOUT_PARENT] = tree[None]
#         return res


class MemberListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    position = serializers.CharField(
        source="user.profile.position", read_only=True
    )

    class Meta:
        model = Member
        fields = (
            "id",
            "full_name",
            "department",
            "position",
        )

    def get_full_name(self, obj):
        return obj.user.full_name()


class MemberSerializer(serializers.ModelSerializer):
    image = Base64ImageField(source="user.image")
    subordinates = serializers.ListField(read_only=True)
    without_parent = serializers.ListField(read_only=True)

    class Meta:
        model = Member
        fields = (
            "id",
            "user_id",
            "image",
            "subordinates",
            "without_parent",
        )


class TeamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "description")


class TeamSerializer(serializers.ModelSerializer):
    """Сериалайзер команд"""

    class Meta:
        model = Team
        fields = ("id", "name", "description")


class TeamDetailSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "owner", "description", "employees")

    @swagger_serializer_method(serializer_or_field=MemberSerializer)
    def get_employees(self, obj):
        request = self.context.get("request")
        max_deep = request.query_params.get("deep", f"{MAX_DEEP_SUBORDINATES}")
        try:
            max_deep = int(max_deep)
        except ValueError:
            max_deep = MAX_DEEP_SUBORDINATES
        else:
            max_deep = min(max(1, max_deep), MAX_DEEP_SUBORDINATES)

        supervisor = Member.objects.get(team=obj, user=obj.owner)
        children = (
            Member.objects.filter(team=obj, user__is_active=True)
            .exclude(id=supervisor.id)
            .select_related("user__profile")
        ).only(
            "id",
            "user_id",
            "user__image",
        )
        return get_tree(children, supervisor, max_deep, MemberSerializer)


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "description")


class TeamShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name")


class ProjectDetailSerializer(serializers.ModelSerializer):
    teams = TeamShortSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "teams", "started", "ended")


class ProjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name")


def get_tree(children, owner, max_deep, serializer):
    tree = defaultdict(list)
    nodes = defaultdict(list)
    for child in children:
        nodes[child.parent_id].append(child)

    def build_subtree(employee, deep=0):
        subtree = serializer(employee).data
        subtree[SUBORDINATES] = []
        for node in nodes[employee.id]:
            if deep + 1 >= max_deep:
                break
            subtree[SUBORDINATES].append(build_subtree(node, deep=deep + 1))
        return subtree

    for parent_id in (owner.id, None):  # owner and non parent
        [
            tree[parent_id].append(build_subtree(node, 0))
            for node in nodes[parent_id]
        ]
    res = serializer(owner).data
    res[SUBORDINATES] = tree[owner.id]
    res[WITHOUT_PARENT] = tree[None]
    return res
