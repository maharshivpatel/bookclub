from django.forms.widgets import HiddenInput
from members.models import Member
from django import forms

class MemberForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs.update({'class': "form-control form-floating mb-3"})
			self.fields['library'].widget = HiddenInput()
			self.fields['library'].disabled = True
	class Meta:
		model = Member
		fields = ['first_name','last_name', 'email', 'phone_number', 'library']