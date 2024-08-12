from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.general.constants import CacheKey
from .models import Member, Team


@receiver(post_save, sender=Team)
def create_team(sender, instance, created, **kwargs):
    cache.delete(CacheKey.TEAMS)
    cache.delete(CacheKey.TEAM_BY_ID % instance.id)


@receiver(post_save, sender=Member)
def update_member(sender, instance, created, **kwargs):
    cache.delete(CacheKey.MEMBERS)
    cache.delete(CacheKey.TEAM_BY_ID % instance.team.id)
    cache.delete(CacheKey.MEMBERS_TEAM_BY_ID % instance.team.id)

    departments = cache.get(CacheKey.DEPARTMENTS)
    if departments:
        departments.add(instance.department.name)
        cache.set(CacheKey.DEPARTMENTS, departments)
