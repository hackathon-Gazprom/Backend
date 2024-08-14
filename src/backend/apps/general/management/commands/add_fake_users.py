import os
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management import BaseCommand, call_command

User = get_user_model()

MAN_NAMES = [
    "Алексей",
    "Николай",
    "Александр",
    "Павел",
    "Илья",
    "Владимир",
    "Денис",
    "Иван",
    "Константин",
    "Сергей",
    "Дмитрий",
    "Михаил",
    "Андрей",
    "Виктор",
    "Роман",
    "Виталий",
    "Петр",
    "Олег",
    "Максим",
    "Сидор",
    "Артем",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("loaddata", "users.json")
        for user in User.objects.all():
            user.set_password(user.password)

            base_dir = settings.BASE_DIR / "data"

            if user.first_name in MAN_NAMES:
                base_dir = base_dir / "M"
            else:
                base_dir = base_dir / "F"

            files = os.listdir(base_dir)
            file_path = base_dir / random.choice(files)
            with file_path.open(mode="rb") as f:
                user.image = File(
                    f,
                    name=user.email.split("@")[0] + file_path.suffix,
                )
                user.save()
