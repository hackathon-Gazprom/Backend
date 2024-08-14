from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from api.fields import Base64ImageField
from api.v1.projects.constants import (
    MAX_DEEP_SUBORDINATES,
    SUBORDINATES,
    WITHOUT_PARENT,
)
from apps.general.constants import CacheKey
from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Member, Project, Team

User = get_user_model()


class ProjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
        )


class TeamShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = (
            "id",
            "name",
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


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Сериалайзер для смены статуса"""

    status = serializers.ChoiceField(choices=Project.Status.choices)

    class Meta:
        model = Project
        fields = (
            "id",
            "status",
        )


class MemberTreeSerializer(serializers.ModelSerializer):
    member_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects)

    class Meta:
        model = Team
        fields = ("member_id", "parent_id")

    def validate(self, attrs):
        member = attrs.get("member_id")
        parent = attrs.get("parent_id")
        errors = defaultdict(list)
        if member == parent:
            errors["member_id"].append(
                "Участник не может быть в подчинении у себя же."
            )

        if member.parent == parent:
            errors["member_id"].append(
                f"Участник уже в подчинении у `{parent}`."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        member = validated_data.get("member_id")
        parent = validated_data.get("parent_id")
        member_id = member.id
        parent_id = parent.id

        members = cache.get(
            CacheKey.MEMBERS_TEAM_BY_ID.format(team_id=instance.id)
        )
        if members is None:
            members = instance.members.values_list("parent_id", "id")
            cache.set(
                CacheKey.MEMBERS_TEAM_BY_ID.format(team_id=instance.id),
                members,
            )

        tree = defaultdict(list)
        for p_id, pk in members:
            tree[p_id].append(pk)

        if parent_id not in tree:
            raise serializers.ValidationError(
                f"Участник `{parent}`, не привязан к этой команде."
            )
        children = set()

        def dfs(_id):
            if _id in children:
                return

            children.add(_id)
            for child in tree[_id]:
                dfs(child)

        for child_id in tree[member_id]:
            dfs(child_id)

        if parent_id in children:
            raise serializers.ValidationError(
                "Нельзя сменить руководителя, который находится в подчинении."
            )

        member.parent = parent
        member.save()
        return instance


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


class MemberCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления пользователя в команду"""

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user"
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source="parent"
    )

    class Meta:
        model = Member
        fields = ("team", "user_id", "parent_id")
        read_only_fields = ("team",)


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

    projects = ProjectShortSerializer(many=True, read_only=True)

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

        print(obj, obj.id, obj.owner, obj.owner.id)

        supervisor = (
            Member.objects.select_related("user")
            .only(
                "id",
                "parent_id",
                "user_id",
                "user__image",
            )
            .get(team=obj, user=obj.owner)
        )
        children = (
            Member.objects.filter(team=obj, user__is_active=True)
            .exclude(id=supervisor.id)
            .select_related("user")
        ).only(
            "id",
            "parent_id",
            "user_id",
            "user__image",
        )
        return get_tree(children, supervisor, max_deep, MemberTeamSerializer)


class ProjectGetSerializer(serializers.ModelSerializer):
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


class ProjectTeamUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения в свагере необходимых полей
    при изменении или удалении команды
    """

    team_id = serializers.PrimaryKeyRelatedField(queryset=Team.objects)

    class Meta:
        model = Project
        fields = ("id", "team_id")


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


# todo: из конструктора команды исключить людей состоящих в команде
