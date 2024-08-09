# Generated by Django 4.2.14 on 2024-08-09 12:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0009_remove_project_teams"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="teams",
            field=models.ManyToManyField(
                related_name="projects",
                through="projects.ProjectTeam",
                to="projects.team",
            ),
        ),
    ]
