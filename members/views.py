from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from members.models import Member
from transactions.models import WalletTransacton
from members.forms import MemberForm
from transactions.forms import MoneyForm
from django.contrib import messages
from bookclub.utils import handle_data, handle_filters
from django.shortcuts import get_object_or_404

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
			'field_name': 'wallet__balance',
			'field_title': 'Balance / Due',
			'css_class': 'text-success currency-pn',
		}
	]
	
	member_initial={'library': request.user.library}
	
	addmoney_initial = {
			'library': request.user.library,
			'created_by': request.user,
			'is_add_balance': True
	}
	
	addmoney_form = MoneyForm(initial=addmoney_initial)
	
	form = MemberForm(initial=member_initial)

	member_modals = [
		{
			'modal_id': 'createMemberModal',
			'modal_title': 'Create New Member',
			'p_btn_txt': 'Create',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			'submit_url_name': 'memberscreate',
			'form': form,
		},
		{
			'modal_id': 'addMoneyModal',
			'modal_title': 'Add Money',
			'p_btn_txt': 'Add',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			'form': addmoney_form,
			'submit_url_name': 'moneyadd',
		},
	]

	filters = handle_filters(request, fields)

	fieldlist = [ field['field_name'] for field in fields ]

	members = Member.objects.filter(library=request.user.library, **filters).values(*fieldlist)
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
		},
		{
			'field_name': 'wallet__balance',
			'field_title': 'Balance / Due',
			'css_class': 'text-success currency-pn',
		},
		{
			'field_name': 'phone_number',
			'field_title': 'Phone Number',
		}
	]

	member = get_object_or_404(Member.objects.filter(library = request.user.library, id=id))

	notes = list(WalletTransacton.objects.filter(member_id=id).values('note'))

	form = MemberForm(request.POST or None, instance=member)

	edit_member_modal = [
		{
			'modal_id': 'editMemberModal',
			'modal_title': 'Edit Member Details',
			'p_btn_txt': 'Update',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			'submit_url_name': 'membersedit',
			'obj_url_id': id,
			'form': form,
		},
	]


	list_of_fields = [ field['field_name'] for field in fields ]
	member = Member.objects.filter(library=request.user.library, id=id).values(*list_of_fields)
	
	if len(member) == 0:
		messages.add_message(request, messages.WARNING, f"Detail Page for this member doesn't exist or you don't have access to it.")
		return redirect('members')

	data = handle_data( fields, member)

	return render(request, 'library/details.html', {'page': page, 'fields': fields, 'data': data, 'modals': edit_member_modal, 'notes': notes })


@login_required
def memberscreate_view(request):
	initial = {
		'library': request.user.library,
	}
	if request.method == "POST":
		form = MemberForm(request.POST or None, initial=initial)
		form.library = request.user.library

	
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, "Member added")
			return redirect('members')

	
		if form.is_bound:
			return render(request, 'library/page_edit.html', {'form': form})
	
	messages.add_message(request, messages.ERROR, "Woah, You visited add Member page! you shouldn't do that.")
	return redirect('members') 



@login_required
def membersedit_view(request, id):

	if request.method == "POST":
		member = get_object_or_404(Member.objects.filter(library = request.user.library, id=id))
		form = MemberForm(request.POST or None, instance=member)
		form.library = request.user.library
	
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, "Member Details Edited Successfully")
			return redirect('membersdetail', id=id)
	
		if form.is_bound:
			return render(request, 'library/page_edit.html', {'form': form})
	
	messages.add_message(request, messages.ERROR, "Woah, You visited edit Member page! you shouldn't do that.")
	return redirect('members') 


@login_required
def membersdelete_view(request, id):
	if request.method == 'POST':
		member = get_object_or_404(Member.objects.filter(library = request.user.library, id=id))
		member.delete()
		messages.add_message(request, messages.SUCCESS, f"{member.full_name} was deleted Successfully.")
		return redirect('members') 
	messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that.")
	return redirect('membersdetail', id=id) 