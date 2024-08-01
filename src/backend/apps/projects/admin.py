from django.contrib import admin

from .forms import ProjectForm
from .models import Employee, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "started", "ended")
    list_display_links = ("id", "name")
    form = ProjectForm


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass
