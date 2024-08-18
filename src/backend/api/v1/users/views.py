from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.general.constants import CacheKey
from .paginations import UsersPagination
from .permissions import IsCurrentUserOrAdminPermission
from .serializers import (
    AvatarUserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserMeSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(
    generics.ListCreateAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    pagination_class = UsersPagination
    swagger_tags = ["users"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "list":
            return UserListSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            qs = cache.get(CacheKey.USERS)
            if qs is None:
                qs = User.objects.select_related("profile").only(
                    "id",
                    "email",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "image",
                    "profile__phone",
                    "profile__telegram",
                    "profile__bio",
                    "profile__position",
                    "profile__birthday",
                    "profile__time_zone",
                )
                cache.set(CacheKey.USERS, qs)
            return qs
        return User.objects.all()

    def get_object(self):
        cache_key = CacheKey.USER_BY_ID.format(user_id=self.kwargs.get("pk"))
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = super().get_object()
            cache.set(cache_key, queryset)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            permissions_classes = [permissions.IsAdminUser]
        else:
            permissions_classes = [IsCurrentUserOrAdminPermission]

        return [permission() for permission in permissions_classes]

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def update_me(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def avatar(self, request):
        serializer = AvatarUserSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
