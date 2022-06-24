from django import forms
from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import UserCreationForm
from library.models import Library, Librarian

class LibrarianCreationForm(UserCreationForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs.update( { 'class': "form-control form-floating mb-3" } )
	
	class Meta:
		model = Librarian
		fields =  [ 'first_name', 'last_name', 'username', 'password1', 'password2']


class LibrarianLoginForm(forms.Form):

		username = forms.CharField( max_length = 30, widget=forms.TextInput( attrs={'class': 'form-floating form-control mb-3', 'autofocus': True} ))
		password = forms.CharField( widget = forms.PasswordInput(attrs={'class': 'form-floating form-control mb-3'}) )


class LibrarianUpdateForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):	
		super().__init__(*args, **kwargs)
		
		for field in self.fields.values():
				field.widget.attrs.update({'class': "form-control  py-2 mb-1"})
		
		self.fields['library'].disabled = True
		self.fields['library'].widget = HiddenInput()

	class Meta:
		model = Librarian
		fields =   ['first_name', 'last_name', 'profile_pic', 'email', 'library']


class LibraryForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs.update( { 'class': "form-control form-floating mb-3" } )

	class Meta:
		model = Library
		fields = '__all__'


class LibrarySelectForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['library'].widget.attrs.update({'class': "form-control form-floating mb-3", 'required': True})
	
	class Meta:
		model = Librarian
		fields = ['library']


