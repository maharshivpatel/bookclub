from django.db import models
from library.models import Library, Librarian
from books.models import Book
from members.models import Member


class Transaction(models.Model):
    member = models.ForeignKey(Member, related_name='transaction', on_delete=models.CASCADE)
    library = models.ForeignKey(Library, related_name='transaction', on_delete=models.CASCADE)
    trans_amount = models.DecimalField('Amount',  max_digits=6, decimal_places=2, blank=True, null=True, default=0) # editable=False
    created_by = models.ForeignKey(Librarian, related_name='transaction', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    book = models.ForeignKey(Book, related_name='transaction', on_delete=models.CASCADE)
    # duration is only useful if want to implement extra features like show time if less than 1 day
    duration = models.DurationField('Rent Duration', null=True, blank=True, editable=False) 
    is_return = models.BooleanField('Is Return ?', default=False)
    is_lost = models.BooleanField('Is Lost / Damaged ?', default=False)
    issue_date = models.DateTimeField('Book Issued on', auto_now_add=True)
    return_date = models.DateTimeField('Book Returned on',  blank=True, editable=False, null=True)

    class Meta:
        ordering = ['-modified',]
    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # store initial values to avoid unneccesary database calls
            self.initial_is_return = self.is_return
            self.initial_is_lost = self.is_lost
            self.initial_trans_amount = self.trans_amount

    def __str__(self):
        name = self.member.full_name or ' '.join((self.member.first_name, self.member.first_name))
        name += ' '
        name += self.book.title
        name += ' (Returned)' if self.is_return else ''
        name += ' (Lost)' if self.is_lost else ''
        return name


class WalletTransacton(models.Model):
    member = models.ForeignKey(Member, related_name='wallet_trans', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Librarian, verbose_name="Librarian", related_name='wallet_trans', on_delete=models.CASCADE)
    is_add_balance = models.BooleanField('Is Add Money Transaction ?',  default=False)
    transaction = models.ForeignKey(Transaction, related_name='wallet_trans', on_delete=models.CASCADE, blank=True, null=True)
    balance_before = models.DecimalField('Value before Transaction',  max_digits=6, decimal_places=2, editable=False, blank=True)
    trans_amount = models.DecimalField('Transaction Amount',  max_digits=6, decimal_places=2, blank=True, null=True)
    balance_after = models.DecimalField('Value after Transaction',  max_digits=6, decimal_places=2, editable=False, blank=True)
    note = models.TextField('Transaction Note', blank=True, null=True)

    class Meta:
        ordering = ['-created',]

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # store initial values to avoid unneccesary database calls
            self.initial_trans_amount = self.trans_amount

    def __str__(self):
        name = self.member.full_name or ' '.join((self.member.first_name, self.member.first_name))
        name += ' | '
        name += str(self.balance_before) 
        name += str('+' + str(self.trans_amount) if self.trans_amount > 0 else str(self.trans_amount) )
        name += ' = ' + str(self.balance_after)
        return name