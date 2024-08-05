from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.projects.models import Project
from .paginations import ProjectsPagination
from .permissions import OwnerOrAdminPermission
from .serializers import (
    ProjectSerializer,
    ProjectStatusSerializer,
)


class ProjectViewSet(ListCreateAPIView, RetrieveUpdateAPIView, GenericViewSet):
    queryset = Project.objects.all()
    pagination_class = ProjectsPagination
    permission_classes = [OwnerOrAdminPermission]
    serializer_class = ProjectSerializer
    swagger_tags = ["projects"]

    # def get_serializer_class(self):
    #     if self.action == "retrieve":
    #         return ProjectDetailSerializer
    #     elif self.action in ("create", "partial_update", "update"):
    #         return ProjectSerializer
    #     return ProjectListSerializer

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)
        # Employee.objects.get_or_create(
        #     project=instance,
        #     user=self.request.user,
        # )

    @action(detail=True, methods=["patch"])
    def change_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectStatusSerializer(
            instance=instance, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        data = serializer.data
        data["status"] = instance.get_status_display()

        return Response(data)

    @action(detail=True, methods=["patch"])
    def change_owner(self, request, *args, **kwargs):
        # TODO: change owner
        pass

    @action(detail=True, methods=["post"])
    def change_employee(self, request, *args, **kwargs):
        # TODO: change employer
        pass


# TODO: Команды список, детально структура
