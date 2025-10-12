# signals.py
from django.db.models.signals import post_save   # this is called when a model's save() method is called   
from django.dispatch import receiver              # this is a decorator to connect signals to receivers
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)          # when a User is created 
def create_profile(sender, instance, created, **kwargs):     # the sender is the model class, instance is the actual instance being saved, created is a boolean indicating whether a new record was created
    if created:                        # if a new User is created
        Profile.objects.create(user=instance)   # create a Profile for that user

@receiver(post_save, sender=User)     # when a User is saved
def save_profile(sender, instance, **kwargs):    # the sender is the model class, instance is the actual instance being saved
    instance.profile.save()   # save the associated Profile



