from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def user_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def profile_after_save(sender, instance, **kwargs):
    cities = cache.get("cities")
    cities.add(instance.city)
    cache.set("cities", cities, None)
