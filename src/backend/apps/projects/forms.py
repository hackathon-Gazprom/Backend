from django import forms
from django.utils import timezone

from apps.projects.constants import GREATER_THAN_ENDED_DATE, LESS_THAN_TODAY
from apps.projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "owner", "description", "started", "ended"]

    def clean(self):
        cd = self.cleaned_data
        started = cd["started"]
        if timezone.now().date() > started:
            self.add_error("started", LESS_THAN_TODAY)
        if started > cd["ended"]:
            self.add_error("started", GREATER_THAN_ENDED_DATE)

        return cd
