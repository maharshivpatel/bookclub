from django import forms
from django.forms.widgets import HiddenInput
from books.models import Book
from members.models import Member
from transactions.models import Transaction, WalletTransacton

class IssueBookForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		initial = kwargs.get('initial', {})

		library = initial['library']
		
		for field in self.fields.values():	
			field.widget.attrs.update({'class': "form-control form-floating mb-3"})

		self.fields['created_by'].widget = HiddenInput()
		self.fields['created_by'].disabled = True
		self.fields['library'].widget = HiddenInput()
		self.fields['library'].disabled = True
		self.fields['member'].queryset = Member.objects.filter(library=library)
		self.fields['book'].queryset = Book.objects.filter(library=library)

	class Meta:
		model = Transaction
		fields = ['member','book', 'library', 'created_by']


class MoneyForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		initial = kwargs.get('initial', {})

		library = initial['library']
		
		for field in self.fields.values():	
			field.widget.attrs.update({'class': "form-control form-floating mb-3"})

		self.fields['created_by'].widget = HiddenInput()
		self.fields['created_by'].disabled = True
		self.fields['is_add_balance'].widget = HiddenInput()
		self.fields['is_add_balance'].disabled = True
		self.fields['member'].queryset = Member.objects.filter(library=library)

	class Meta:
		model = WalletTransacton
		fields = ['member', 'trans_amount', 'note', 'is_add_balance', 'created_by']