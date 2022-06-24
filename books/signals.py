from django.dispatch import receiver
from django.forms import ValidationError
from books.models import Book
from transactions.models import Transaction
from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed


def stock_controller(book, library, instance, created: bool = False, deleted: bool = False):

	initial_is_return = instance.initial_is_return
	is_return = instance.is_return
	initial_is_lost = instance.initial_is_lost
	is_lost = instance.is_lost


	def instock_to_rented():
		book.instock_qty -= 1
		library.books_instock -= 1
		book.rented_out_qty += 1
		library.books_rented_out += 1 
		return

	def rented_to_instock():
		book.rented_out_qty -= 1
		library.books_rented_out -= 1
		book.instock_qty += 1
		library.books_instock += 1
		return

	def rented_to_lost():
		book.rented_out_qty -= 1
		library.books_rented_out -= 1
		book.lost_qty += 1
		library.books_lost += 1
		return

	def lost_to_instock():
		book.lost_qty -= 1
		library.books_lost -= 1
		book.instock_qty += 1
		library.books_instock += 1
		return

	def instock_to_lost():
		book.instock_qty -= 1
		library.books_instock -= 1
		book.lost_qty += 1
		library.books_lost += 1
		return

	if created: return instock_to_rented();

	if deleted and initial_is_lost: return lost_to_instock();

	if deleted and not initial_is_return: return rented_to_instock();

	#  handle reversal of is_lost and is_return if user made mistake and is trying to fix it.
	if is_lost and not initial_is_lost and initial_is_return and not is_return: return instock_to_lost();
	
	if is_return and not initial_is_return and initial_is_lost and not is_lost: return lost_to_instock();

	if is_return and not initial_is_return: return rented_to_instock();

	if is_lost and not initial_is_lost: return rented_to_lost();

	# once book is_returned not returning is not allowed as user can issue the book again.
	# if not is_return and initial_is_return:

	if initial_is_lost and not is_lost: return lost_to_instock();


@receiver(pre_save, sender=Book)
def before_book_save(instance, **kwargs):
	if not instance.pk:
		instance.library.books_instock += instance.instock_qty
		instance.library.save()
	else:
		change_in_qty = instance.instock_qty - instance.initial_instock_qty
		instance.library.books_instock += change_in_qty
		instance.library.save()


@receiver(pre_delete, sender=Book)
def before_book_delete(instance, **kwargs):
	if instance.rented_out_qty != 0:
		raise ValidationError('This book is still rented to Members you can\'t delete it.')
	instance.library.books_instock -= instance.instock_qty
	instance.library.save()



@receiver(m2m_changed, sender=Book.publishers.through)
def book_publiser_m2m_changed(instance, action, **kwargs):

	if action in ('post_add', 'post_remove'):
		instance.publishers_text = ' / '.join(
			[
				fn['full_name']
					for fn
					in instance.publishers.all()
					.values('full_name')
				]
		)
		instance.save()


@receiver(m2m_changed, sender=Book.authors.through)
def book_authors_m2m_changed(instance, action, **kwargs):

	if action in ('post_add', 'post_remove'):
		instance.authors_text = ' / '.join(
			[
				fn['full_name']
				for fn
				in instance.authors.all()
				.values('full_name')
				]
		)
		instance.save()


@receiver(post_save, sender=Transaction)
def after_transaction_save(instance, created, **kwargs):

	book = Book.objects.filter(
		pk=instance.book.id,
		library_id=instance.library.id
		).first()

	stock_controller(book, instance.library, instance, created)

	book.save()
	instance.library.save()


@receiver(pre_delete, sender=Transaction)
def before_transaction_delete(instance, **kwargs):

	book = Book.objects.filter(
		pk=instance.book.id,
		library_id=instance.library.id
		).first()

	stock_controller(book, instance.library, instance, deleted=True)