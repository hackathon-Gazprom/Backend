from django import forms
from django.utils import timezone

from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Member, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "owner",
            "description",
            "started",
            "ended",
            "teams",
        ]

    def clean(self):
        cd = self.cleaned_data
        started = cd["started"]
        if self.instance.id is None and timezone.now().date() > started:
            self.add_error("started", LESS_THAN_TODAY)
        if self.instance.id is not None and "started" in self.changed_data:
            self.add_error("started", "Нельзя изменять начальную дату")
        if started > cd["ended"]:
            self.add_error("started", GREATER_THAN_ENDED_DATE)

        return cd


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["team", "user", "department", "parent"]

    def clean(self):
        cd = self.cleaned_data
        team = cd["team"]
        parent = cd["parent"]
        if parent is not None and team != parent.team:
            self.add_error(
                "parent", f"parent team must be equal to {str(team)!r}"
            )
        return super().clean()
