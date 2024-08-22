from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cliente

@receiver(post_save, sender=Cliente)
def create_user_for_cliente(sender, instance, created, **kwargs):
    if created:
        # Create a user linked to the Cliente instance
        user = User.objects.create_user(username=instance.email, email=instance.email)
        instance.usuario = user
        instance.save()