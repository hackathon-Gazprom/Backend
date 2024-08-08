from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from apps.projects.models import Member, Project, Team
from .filters import MemberFilter
from .paginations import ProjectsPagination
from .permissions import OwnerOrAdminPermission
from .serializers import (
    MemberSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectSerializer,
    ProjectStatusSerializer,
    TeamDetailSerializer,
    TeamSerializer,
)


class ProjectViewSet(ListCreateAPIView, RetrieveUpdateAPIView, GenericViewSet):
    queryset = Project.objects.all()
    pagination_class = ProjectsPagination
    permission_classes = [OwnerOrAdminPermission]
    swagger_tags = ["projects"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProjectDetailSerializer
        elif self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

    # @action(detail=True, methods=["patch"])
    # def change_owner(self, request, *args, **kwargs):
    #     pass  # TODO: change owner

    # @action(detail=True, methods=["post"])
    # def change_employee(self, request, *args, **kwargs):
    #     pass  # TODO: change employer


class TeamViewSet(ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    swagger_tags = ["teams"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamSerializer


class MemberViewSet(ReadOnlyModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = MemberFilter
    search_fields = [
        "^user__first_name",
        "^user__last_name",
        "^user__middle_name",
    ]
    swagger_tags = ["members"]
