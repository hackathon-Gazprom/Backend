from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("loaddata", "users.json")
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()
