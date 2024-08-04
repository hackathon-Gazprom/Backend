from django.contrib import admin
from django.contrib.admin import display

from .forms import ProjectForm
from .models import Employee, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "started", "ended")
    list_display_links = ("id", "name")
    form = ProjectForm


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "user", "parent_display")
    list_display_links = ("id", "project", "user")
    list_filter = ("project",)
    search_fields = ("user__email",)

    @display(description="Руководитель")
    def parent_display(self, obj):
        return obj.parent.user if obj.parent else None
