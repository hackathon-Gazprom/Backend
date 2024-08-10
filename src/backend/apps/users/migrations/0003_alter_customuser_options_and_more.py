# Generated by Django 4.2.14 on 2024-08-10 11:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_profile_city"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customuser",
            options={
                "ordering": ["last_name", "first_name", "middle_name"],
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
        ),
        migrations.AddIndex(
            model_name="customuser",
            index=models.Index(
                fields=["first_name", "last_name", "middle_name"],
                name="users_custo_first_n_a222dc_idx",
            ),
        ),
    ]
