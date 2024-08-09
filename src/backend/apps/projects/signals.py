from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Member, Team


@receiver(post_save, sender=Team)
def create_team(sender, instance, created, **kwargs):
    cache.delete("teams")
    cache.delete(f"team:{instance.id}")


@receiver(post_save, sender=Member)
def update_member(sender, instance, created, **kwargs):
    cache.delete(f"members:team:{instance.team.id}")
