from collections import defaultdict

from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from api.fields import Base64ImageField
from api.v1.projects.constants import (
    MAX_DEEP_SUBORDINATES,
    SUBORDINATES,
    WITHOUT_PARENT,
)
from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Member, Project, ProjectTeam, Team

User = get_user_model()


class ProjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
        )


class ProjectTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTeam
        fields = ("id",)

    def to_representation(self, instance):
        return ProjectShortSerializer(instance.project).data


class TeamShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = (
            "id",
            "name",
        )


class TeamProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTeam
        fields = ("id",)

    def to_representation(self, instance):
        return TeamShortSerializer(instance.team).data


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
        fields = (
            "id",
            "status",
        )


class MemberSerializer(serializers.ModelSerializer):
    """Сериалайзер сотрудников"""

    department = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )
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


class MemberTeamSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения структуры команды"""

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


class TeamSerializer(serializers.ModelSerializer):
    """Сериалайзер команд"""

    projects = ProjectTeamSerializer(
        many=True, read_only=True, source="project_team"
    )

    class Meta:
        model = Team
        fields = ("id", "name", "projects")


class TeamDetailSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "owner", "description", "employees")

    @swagger_serializer_method(serializer_or_field=MemberTeamSerializer)
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
        return get_tree(children, supervisor, max_deep, MemberTeamSerializer)


class ProjectListSerializer(serializers.ModelSerializer):
    teams = TeamProjectSerializer(
        many=True, read_only=True, source="project_team"
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "teams",
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    teams = TeamShortSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "teams",
            "started",
            "ended",
        )


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
