from django.db import models


class CreatedField(models.Model):
    created = models.DateTimeField("Создано", auto_now_add=True)
    updated = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        abstract = True
