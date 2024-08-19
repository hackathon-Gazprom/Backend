import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.cache import cache
from rest_framework import serializers

from api.fields import Base64ImageField
from api.v1.projects.serializers import ProjectShortSerializer
from api.v1.users.constants import (
    ERROR_PHONE,
    ERROR_TELEGRAM,
    ERROR_TIMEZONE,
    TELEGRAM_PATTERN,
)
from apps.general.constants import CacheKey
from apps.projects.models import Member, Project, Team
from apps.users.constants import MAX_TIMEZONE, MIN_TIMEZONE, RE_PHONE
from apps.users.models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения профиля"""

    class Meta:
        model = Profile
        fields = (
            "phone",
            "telegram",
            "bio",
            "position",
            "birthday",
            "time_zone",
        )


class UserFullNameMixin:
    """Миксин для ФИО"""

    full_name = serializers.SerializerMethodField(read_only=True)

    def get_full_name(self, obj):
        return obj.full_name()


class AvatarUserSerializer(serializers.ModelSerializer):
    """Сериалайзер для смены аватара"""

    image = Base64ImageField()

    class Meta:
        model = User
        fields = ("image",)


class UserListSerializer(UserFullNameMixin, serializers.ModelSerializer):
    """Сериалайзер для списка пользователей"""

    position = serializers.CharField(source="profile.position", read_only=True)
    department = serializers.CharField(default="")

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "position",
            "department",
        )

    def get_full_name(self, obj):
        return obj.full_name()


class UserDetailSerializer(UserFullNameMixin, serializers.ModelSerializer):
    """Сериалайзер пользователя"""

    profile = ProfileSerializer()
    projects = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "image",
            "profile",
            "projects",
        )

    def get_projects(self, user):
        projects = Project.objects.filter(
            teams__in=Member.objects.filter(user=user).values_list(
                "team_id", flat=True
            )
        ).only("id", "name")
        return ProjectShortSerializer(projects, many=True).data


class UserSerializer(UserFullNameMixin, serializers.ModelSerializer):
    """Сериалайзер пользователя"""

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "image",
            "profile",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер создания пользователя"""

    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ("email", "password")

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserMeSerializer(UserFullNameMixin, serializers.ModelSerializer):
    """Сериализатор для отображения собственной информации пользователя"""

    profile = ProfileSerializer()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "image",
            "profile",
            "projects",
        )

    def get_projects(self, obj):
        my_projects = cache.get(CacheKey.MY_PROJECTS.format(user_id=obj.id))
        if my_projects is None:
            my_projects = set(
                Team.objects.filter(
                    members__user=obj,
                ).values_list("projects__name", flat=True)
            )
            cache.set(CacheKey.MY_PROJECTS.format(user_id=obj.id), my_projects)
        return sorted(my_projects)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для обновления данных пользователя"""

    bio = serializers.CharField(source="profile.bio")
    birthday = serializers.DateField(source="profile.birthday")
    phone = serializers.CharField(source="profile.phone")
    position = serializers.CharField(source="profile.position")
    telegram = serializers.CharField(source="profile.telegram")
    time_zone = serializers.IntegerField(source="profile.time_zone")

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "telegram",
            "bio",
            "birthday",
            "position",
            "time_zone",
        )

    def validate_telegram(self, data):
        exp = re.compile(TELEGRAM_PATTERN)
        if not exp.match(data):
            raise serializers.ValidationError(ERROR_TELEGRAM)
        return data

    def validate_time_zone(self, data):
        if data < MIN_TIMEZONE or data > MAX_TIMEZONE:
            raise serializers.ValidationError(ERROR_TIMEZONE)
        return data

    def validate_phone(self, data):
        exp = re.compile(RE_PHONE)
        if not exp.match(data):
            raise serializers.ValidationError(ERROR_PHONE)
        return data

    def update(self, instance, validated_data):
        profile_data = {}
        if "profile" in validated_data:
            profile_data = validated_data.pop("profile")
        for key, value in profile_data.items():
            setattr(instance.profile, key, value)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data
