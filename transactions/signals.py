from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from transactions.models import Transaction, WalletTransacton
from django.utils.timezone import now
from django.core.exceptions import ValidationError


def wallet_controller(instance):

	if instance.is_return and not instance.initial_is_return:
		instance.duration = instance.return_date - instance.issue_date
		days = instance.duration.days + 1
		instance.trans_amount = instance.book.rent_fee * days

	if instance.is_lost and not instance.initial_is_lost:
		instance.trans_amount = instance.book.book_value


@receiver(pre_save, sender=Transaction)
def before_transaction_save(instance, **kwargs):
	if ( 
		not instance.pk
		and
		( instance.book.instock_qty == 0 )
	):
		raise ValidationError(f"You don't have {instance.book.title} book in stock.")

	if (
		(
			instance.member.transaction.all()
			.filter(
				is_return=False,
				is_lost=False,
			)
			.count()
			>=
			instance.library.max_book
		)
		and not instance.pk
	):
		raise ValidationError(f"Member can't have books more than {instance.created_by.library.max_book_person} at a time.")

	if (
			(
					instance.member.wallet.balance
				<	-(instance.library.max_debt_allowed - 1)
			)
			and not instance.pk
	):
		raise ValidationError(f"Member can't have debt of more than ₹ {instance.created_by.library.max_debt_allowed}.")

	
	if not instance.pk:
			# safegaurd
			instance.is_return, instance.is_lost = False, False
			
			if (
				instance.book.transaction.all()
				.filter(
					is_return=False,
					is_lost=False,
				)
				.count()
				!= 0
			):
				raise ValidationError("This User have already rented this book.")
	
	if (
			(
					instance.is_return and not instance.initial_is_return
				or  instance.is_lost and not instance.initial_is_lost
			)
			and instance.pk
	):
		instance.return_date = now()

		if (
			instance.pk
			and (
					instance.is_return and not instance.initial_is_return
				or	instance.is_lost and not instance.initial_is_lost
			)
		):
			wallet_controller(instance)

	# safegaurd
	if instance.is_return and instance.is_lost:
		raise ValidationError("Book can't be Lost/Damaged & Returned at the same time")

	# This code is just for safegaurd and below if statements should never be true.
	if instance.initial_is_return and (instance.is_lost == instance.initial_is_lost): instance.is_return = True;
	if instance.initial_is_lost and (instance.is_return == instance.initial_is_return): instance.is_lost = True;


@receiver(post_save, sender=Transaction)
def after_transaction_save(instance, **kwargs):
	if (
		(
				instance.is_return
			or  instance.initial_is_return
			or  instance.is_lost
			or  instance.initial_is_lost
		)
		and instance.pk
	):
		if (
                	instance.is_return != instance.initial_is_return
                and	instance.is_lost != instance.initial_is_lost
            ):
				last_wallet_trans = (
					WalletTransacton.objects.filter(
						transaction_id=instance.id
					).last()
				)
				orignal_trans = Transaction.objects.get( id=instance.id )

				orignal_trans.trans_amount = last_wallet_trans.trans_amount
				
				WalletTransacton.objects.create(
					member=instance.member,
					transaction=orignal_trans,
					created_by=instance.created_by
				)
		WalletTransacton.objects.create(
			member=instance.member,
			transaction=instance,
			created_by=instance.created_by,
		)


@receiver(pre_save, sender=WalletTransacton)
def before_wallet_transaction_save(instance, **kwargs):
	if (
			not instance.pk
		and not instance.is_add_balance
	):
		instance.balance_before = instance.member.wallet.balance
		instance.trans_amount = -instance.transaction.trans_amount
		instance.member.wallet.balance = instance.balance_before + instance.trans_amount
		instance.balance_after = instance.member.wallet.balance
		instance.member.wallet.save()

	elif (
		not instance.pk
		and instance.is_add_balance
	):
		instance.balance_before = instance.member.wallet.balance
		instance.member.wallet.balance += instance.trans_amount
		instance.balance_after = instance.member.wallet.balance
		instance.member.wallet.save()

	else:
		# safegaurd
		raise ValidationError('You can\'t edit Wallet Transaction')

@receiver(post_delete, sender=WalletTransacton)
def after_wallet_transaction_delete(instance, **kwargs):

	instance.member.wallet.balance -= instance.trans_amount
	instance.member.wallet.save()