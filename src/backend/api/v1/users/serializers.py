import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers

from api.fields import Base64ImageField
from api.v1.users.constants import (
    ERROR_PHONE,
    ERROR_TELEGRAM,
    ERROR_TIMEZONE,
    TELEGRAM_PATTERN,
)
from apps.users.constants import MAX_TIMEZONE, MIN_TIMEZONE, RE_PHONE
from apps.users.models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Сериалайзер профиля"""

    class Meta:
        model = Profile
        fields = ("phone", "telegram", "bio", "birthday", "time_zone")


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер пользователя"""

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "image",
            "profile",
        )


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для обновления данных пользователя"""

    bio = serializers.CharField(source="profile.bio")
    birthday = serializers.DateField(source="profile.birthday")
    phone = serializers.CharField(source="profile.phone")
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
        profile_data = validated_data.pop("profile")
        for key, value in profile_data.items():
            setattr(instance.profile, key, value)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


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


class AvatarUserSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = User
        fields = ("image",)
