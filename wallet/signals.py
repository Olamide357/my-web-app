'''
# wallet/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from base.models import Transaction
from register.models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_wallet(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from register.models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.save()
'''