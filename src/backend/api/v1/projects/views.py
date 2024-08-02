from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import Employee, Project
from .paginations import ProjectsPagination
from .permissions import OwnerOrAdminPermission
from .serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectSerializer,
    ProjectStatusSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    pagination_class = ProjectsPagination
    permission_classes = [OwnerOrAdminPermission]
    swagger_tags = ["projects"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProjectDetailSerializer
        elif self.action in ("create", "partial_update", "update"):
            return ProjectSerializer
        elif self.action == "change_status":
            return ProjectStatusSerializer
        return ProjectListSerializer

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)
        Employee.objects.get_or_create(
            project=instance,
            user=self.request.user,
            position="Руководитель проекта",
        )

    @action(detail=True, methods=["POST"])
    def change_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        data = serializer.data
        data["status"] = instance.get_status_display()

        return Response(data)

    # TODO: change owner
    # TODO: change employer
