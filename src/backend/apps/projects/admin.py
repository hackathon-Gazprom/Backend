from django.contrib import admin
from django.db import models
from django.utils.text import smart_split

from .forms import ProjectForm, MemberForm
from .models import Department, Member, Project, Team, ProjectTeam


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "started", "ended")
    list_display_links = ("id", "name")
    form = ProjectForm
    raw_id_fields = ("owner",)
    filter_horizontal = ("teams",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teams":
            db_field.remote_field.through._meta.auto_created = True
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class MemberInLine(admin.TabularInline):
    model = Member
    show_change_link = True
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "full_name")
    list_display_links = list_display
    form = MemberForm
    inlines = [MemberInLine]
    raw_id_fields = ("team", "user", "parent")
    list_filter = ("team_id",)
    search_fields = ("team_id",)
    team_search_fields = "team_id"

    @admin.display(ordering="user.last_name")
    def full_name(self, obj):
        return obj.user.full_name()

    def get_search_results(self, request, queryset, search_term):
        term_queries = []
        for bit in smart_split(search_term):
            or_queries = models.Q.create(
                [("team_id", bit)],
                connector=models.Q.OR,
            )
            term_queries.append(or_queries)
        queryset = queryset.filter(models.Q.create(term_queries))
        return queryset, False


class ProjectTeamAdmin(admin.StackedInline):
    model = ProjectTeam


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner")
    list_display_links = ("id", "name")
    fields = ("name", "owner", "description")
    raw_id_fields = ("owner",)
    inlines = [ProjectTeamAdmin]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display


@admin.register(ProjectTeam)
class TeamAdmin(admin.ModelAdmin):
    pass
