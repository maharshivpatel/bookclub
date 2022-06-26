from operator import is_
from django.db.models.signals import pre_save, post_save, pre_delete
from django.forms import ValidationError
from transactions.models import Transaction
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


@receiver(pre_delete, sender=Member)
def before_member_delete(instance, **kwargs):
    
    if (0 < Transaction.objects.filter(
            member=instance,
            is_return=False,
            is_lost=False)
        .count()
        ):
        raise ValidationError(f"{instance.full_name} still have rented books. please clear them and try again.")