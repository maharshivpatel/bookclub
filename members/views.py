from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from members.models import Member
from django.contrib import messages
from bookclub.utils import handle_data, handle_filters

@login_required
def members_view(request):
	page = {
		'title': 'Members',
		'buttons': [
		{
			'btn_text':'New Member',
			'button_action': "openmodal",
			'modal_target': "createMemberModal",
			'css_btn_type': 'primary',
		},
		{
			'btn_text':'Add Money',
			'button_action': "openmodal",
			'modal_target': "addMoneyModal",
			'css_btn_type': 'success',
		}
		]
	}

	fields = [
		{
			'field_name': 'id',
			'field_title': 'ID',
		},
		{
			'field_name': 'full_name',
			'field_title': 'Full Name',
			'url_prefix': 'details',
			'html_attr': 'autofocus',
		},
		{
			'field_name': 'phone_number',
			'field_title': 'Phone Number',
		},
		{
			'field_name': 'transaction__book__title',
			'field_title': 'Last Book Rented',
		},
		{
			'field_name': 'transaction__issue_date',
			'field_title': 'Last Rented Date',
		},
		{
			'field_name': 'wallet__balance',
			'field_title': 'Balance / Due',
			'css_class': 'text-success currency-pn',
		}
	]
	
	member_modals = [
		{
			'modal_id': 'createMemberModal',
			'modal_title': 'Create New Member',
			'p_btn_txt': 'Create',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			# 'form': 'django-form-variable-name',
		},
		{
			'modal_id': 'addMoneyModal',
			'modal_title': 'Add Money',
			'p_btn_txt': 'Add',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			# 'form': 'django-form-variable-name',
		}
	]

	filters = handle_filters(request, fields)

	fieldlist = [ field['field_name'] for field in fields ]

	members = Member.objects.filter(**filters).values(*fieldlist)

	data = handle_data( fields, members)

	return render(request, 'library/list.html', {'page': page, 'fields': fields, 'data': data, 'modals': member_modals })


@login_required
def membersdetail_view(request, id):

	page = {
		'title': 'Members',
		'buttons': [
			{
				'btn_text':'Back',
				'button_action': "redirect",
				'url_name': 'members',
				'css_btn_type': 'link',
			},
			{
				'btn_text':'Edit',
				'button_action': 'openmodal',
				'modal_target': 'editMemberModal',
			},
			{
				'btn_text':'Delete',
				'url_name': 'membersdelete',
				'obj_url_id': id,
				'button_action': "post_form",
				'css_btn_type': 'danger',
			}
		]
	}

	fields = [
		{
			'field_name': 'full_name',
			'field_title': 'Full Name',
			'col_span': 8,
			'url_prefix': 'detail',
		},
		{
			'field_name': 'wallet__balance',
			'field_title': 'Balance / Due',
			'css_class': 'text-success currency-pn',
		},
		{
			'field_name': 'phone_number',
			'field_title': 'Phone Number',
		},
		{
			'field_name': 'transaction__issue_date',
			'field_title': 'Last Rented Date',
			'col_span': 8,
		},
		{
			'field_name': 'transaction__book__title',
			'field_title': 'Last Book Rented',
			'col_span': 12,
		},
	]

	edit_member_modal = [
		{
			'modal_id': 'editMemberModal',
			'modal_title': 'Edit Member Details',
			'p_btn_txt': 'Update',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			# 'form': 'django-form-variable-name',
		},
	]


	list_of_fields = [ field['field_name'] for field in fields ]
	member = Member.objects.filter(library=request.user.library, id=id).values(*list_of_fields)
	
	data = handle_data( fields, member)

	return render(request, 'library/details.html', {'page': page, 'fields': fields, 'data': data, 'modals': edit_member_modal })


@login_required
def memberscreate_view(request):
	if request.method == 'POST':
		messages.add_message(request, messages.SUCCESS, f"You have created member")
		return redirect('members') 
	messages.add_message(request, messages.ERROR, "Woah, You visited issue book page! you shouldn't do that.")
	return redirect('members') 


@login_required
def membersedit_view(request, id):
	if request.method == 'POST':
		member = Member.objects.get(id=id, library = request.user.library)
		member.delete()
		messages.add_message(request, messages.SUCCESS, f"{member.full_name} was edited Successfully.")
		return redirect('membersdetail', id=id) 
	messages.add_message(request, messages.ERROR, "Woah, You visited post edit page! you shouldn't do that.")
	return redirect('membersdetail', id=id) 


@login_required
def membersdelete_view(request, id):
	if request.method == 'POST':
		member = Member.objects.get(id=id, library = request.user.library)
		member.delete()
		messages.add_message(request, messages.SUCCESS, f"{member.full_name} was deleted Successfully.")
		return redirect('members') 
	messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that.")
	return redirect('membersdetail', id=id) 