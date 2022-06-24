from django.forms.widgets import HiddenInput
from django import forms
from books.models import Book

class BookForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		for field in self.fields.values():
			field.widget.attrs.update({'class': "form-control mx-1 mb-3"})

			if field.widget.input_type in ('select'):
				field.widget.attrs.update({'class': "form-control form-select mx-1 mb-3"})

		self.fields['library'].disabled = True
		self.fields['library'].widget = HiddenInput()

	class Meta:
		model = Book
		fields = '__all__'