# Generated by Django 4.2.14 on 2024-08-05 16:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="project",
            constraint=models.CheckConstraint(
                check=models.Q(("started__lte", models.F("ended"))),
                name="started_index",
            ),
        ),
    ]
