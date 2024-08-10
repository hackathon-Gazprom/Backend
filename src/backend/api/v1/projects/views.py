from django.core.cache import cache
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
    MemberTreeSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectSerializer,
    ProjectStatusSerializer,
    TeamDetailSerializer,
    TeamSerializer,
)


class ProjectViewSet(ListCreateAPIView, RetrieveUpdateAPIView, GenericViewSet):
    queryset = Project.objects.prefetch_related("teams").only(
        "id",
        "name",
        "description",
        "started",
        "ended",
    )
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

    # @action(detail=True, methods=["post"], url_path="update_team")
    # def add_team_to_project(self, request, *args, **kwargs):
    #     pass  # TODO: add team to project
    #
    # @add_team_to_project.mapping.delete
    # def remove_team_from_project(self, request, *args, **kwargs):
    #     pass


class TeamViewSet(ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    swagger_tags = ["teams"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamSerializer

    def get_queryset(self):
        qs = Team.objects.prefetch_related("projects")
        if self.action == "retrieve":
            cached_qs = cache.get(f"team:{self.kwargs.get('pk', 0)}")
            if cached_qs is None:
                cached_qs = qs.prefetch_related("members").only(
                    "id",
                    "name",
                    "owner",
                    "description",
                )
                cache.set(f"team:{self.kwargs.get('pk', 0)}", cached_qs)
            return cached_qs
        elif self.action == "change_employee":
            return qs.prefetch_related("members").only("id")

        cached_qs = cache.get("teams")
        if cached_qs is None:
            cached_qs = qs.only(
                "id",
                "name",
            )
            cache.set("teams", cached_qs)
        return cached_qs

    @action(
        detail=True,
        methods=["put"],
    )
    def change_employee(self, request, *args, **kwargs):
        serializer = MemberTreeSerializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "ok"})


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

    def get_queryset(self):
        qs = cache.get("members")
        if qs is None:
            qs = Member.objects.select_related(
                "user__profile", "department"
            ).only(
                "id",
                "user__first_name",
                "user__middle_name",
                "user__last_name",
                "department__name",
                "user__profile__position",
                "user__profile__city",
            )
            cache.set("members", qs)
        return qs
