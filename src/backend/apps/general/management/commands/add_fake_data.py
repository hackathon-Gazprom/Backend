from django.core.management import BaseCommand, call_command

from apps.projects.models import Member


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("add_fake_users")
        call_command("loaddata", "departments.json")
        call_command("loaddata", "projects.json")
        call_command("loaddata", "teams.json")
        Member.objects.all().delete()
        call_command("loaddata", "members.json")
        call_command("loaddata", "project_teams.json")
