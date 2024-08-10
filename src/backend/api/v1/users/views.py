from django.contrib.auth import get_user_model
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import Profile
from .paginations import UsersPagination
from .permissions import IsCurrentUserOrAdminPermission
from .serializers import (
    AvatarUserSerializer,
    CitySerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
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

    def get_permissions(self):
        if self.action == "create":
            permissions_classes = [permissions.IsAdminUser]
        elif self.action == "cities":
            permissions_classes = [permissions.AllowAny]
        else:
            permissions_classes = [IsCurrentUserOrAdminPermission]

        return [permission() for permission in permissions_classes]

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

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

    @swagger_auto_schema(
        responses={200: CitySerializer(many=True)},
    )
    @action(
        detail=False,
        methods=["get"],
        pagination_class=None,
    )
    def cities(self, request):
        cities = cache.get("cities")
        if cities is None:
            cities = set(
                Profile.objects.exclude(city="").values_list("city", flat=True)
            )
            cache.set("cities", cities, None)
        return Response(sorted(cities))
