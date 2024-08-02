from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsCurrentUserOrAdminPermission
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
)

User = get_user_model()


class UserUpdateView(
    generics.CreateAPIView, generics.RetrieveAPIView, viewsets.GenericViewSet
):
    queryset = User.objects.all()
    swagger_tags = ["users"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsCurrentUserOrAdminPermission]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            return Response(UserSerializer(request.user).data)

        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
