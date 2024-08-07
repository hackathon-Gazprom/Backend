from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .paginations import UsersPagination
from .permissions import IsCurrentUserOrAdminPermission
from .serializers import (
    AvatarUserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)

User = get_user_model()


# TODO list users, фильтр (ФИО, должность, отдел?) по 12
# TODO list users для фильтра (ФИО + должность)
#  (Подразделение?, должность, город?) по сколько?


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
            return [permissions.IsAdminUser()]
        else:
            return [IsCurrentUserOrAdminPermission()]

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
