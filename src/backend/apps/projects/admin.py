from django.contrib import admin

from .forms import ProjectForm
from .models import Project, Member, Team, Department


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "started", "ended")
    list_display_links = ("id", "name")
    form = ProjectForm
    raw_id_fields = ("owner",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name")
    list_display_links = list_display
    raw_id_fields = ("team", "user", "parent")

    @admin.display(ordering="user.last_name")
    def full_name(self, obj):
        return obj.user.full_name()


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
