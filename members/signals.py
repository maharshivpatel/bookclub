from django.db.models.signals import pre_save, post_save
from members.models import  Member, Wallet
from django.dispatch import receiver

@receiver(pre_save, sender=Member)
def before_member_save(instance, **kwargs):

    instance.full_name = ' '.join((instance.first_name, instance.last_name))

@receiver(post_save, sender=Member)
def after_member_save(instance, created, **kwargs):

    instance.full_name = ' '.join((instance.first_name, instance.last_name))
    
    if not created: return;
    
    Wallet.objects.create(member=instance)