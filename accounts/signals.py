from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile,User

@receiver(post_save, sender=User)
def _post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
    print('user is updated')
