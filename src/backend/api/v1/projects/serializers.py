from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from api.fields import Base64ImageField
from api.v1.projects.constants import MAX_DEEP_SUBORDINATES
from api.v1.projects.utils import get_tree
from apps.general.constants import CacheKey
from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Member, Project, Team

User = get_user_model()


class ProjectShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения проектов"""

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
        )


class TeamShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения команд"""

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
        )


class MemberTeamSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения структуры команды"""

    image = Base64ImageField(source="user.image")
    subordinates = serializers.ListField(read_only=True)
    without_parent = serializers.ListField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    department = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )
    position = serializers.CharField(
        source="user.profile.position", read_only=True
    )

    class Meta:
        model = Member
        fields = (
            "id",
            "user_id",
            "parent_id",
            "full_name",
            "department",
            "position",
            "image",
            "subordinates",
            "without_parent",
        )

    def get_full_name(self, obj):
        return obj.user.full_name()


class ProjectGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения проекта(ов)"""

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


class ProjectTeamUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения в свагере необходимых полей
    при изменении или удалении команды
    """

    team_id = serializers.PrimaryKeyRelatedField(queryset=Team.objects)

    class Meta:
        model = Project
        fields = ("id", "team_id")


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


class MemberTreeSerializer(serializers.ModelSerializer):
    """Сериализатор изменения позиции участника команды"""

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


class TeamSerializer(serializers.ModelSerializer):
    """Сериалайзер команд"""

    projects = ProjectShortSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "projects")


class TeamDetailSerializer(serializers.ModelSerializer):
    """Сериализатор команды"""

    employees = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "owner",
            "description",
            "employees",
        )

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

        qs = (
            Member.objects.filter(team=obj)
            .select_related("user__profile", "department")
            .only(
                "id",
                "parent_id",
                "user_id",
                "user__first_name",
                "user__last_name",
                "user__middle_name",
                "user__image",
                "department",
                "user__profile__position",
            )
        )
        supervisor = qs.get(user=obj.owner)
        children = qs.exclude(user=obj.owner)
        return get_tree(children, supervisor, max_deep, MemberTeamSerializer)


class TeamCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания команды"""

    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects)

    class Meta:
        model = Team
        fields = ("id", "name", "owner")


# todo: из конструктора команды исключить людей состоящих в команде
