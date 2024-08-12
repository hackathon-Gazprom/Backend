from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from ..general.constants import CacheKey
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def user_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def profile_after_save(sender, instance, **kwargs):
    cities = cache.get(CacheKey.CITIES)
    if cities and instance.city:
        cities.add(instance.city)
        cache.set(CacheKey.CITIES, cities)

    positions = cache.get(CacheKey.POSITIONS)
    if positions and instance.position:
        positions.add(instance.position)
        cache.set(CacheKey.POSITIONS, positions)
