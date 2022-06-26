import os, json
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.shortcuts import render, redirect
from transactions.models import Transaction
from members.models import Member
from transactions.models import WalletTransacton
from members.forms import MemberForm
from transactions.forms import MoneyForm
from django.contrib import messages
from bookclub.utils import process_data
from django.shortcuts import get_object_or_404

@login_required
def members_view(request):

	memberadd_initial = {
		'library': request.user.library
	}
	
	moneyadd_initial = {
		'library': request.user.library,
		'created_by': request.user,
		'is_add_balance': True
	}

	modalforms = {
		'moneyadd_form' : MoneyForm(initial=moneyadd_initial),
		'memberadd_form' : MemberForm(initial=memberadd_initial)
	}

	
	pagedata, data = process_data (
		request=request,
		model=Member,
		modalforms=modalforms,
		jsoninfo={'folder': 'members', 'file': 'members'}
	
	)

	return render(request, 'library/list.html', {**pagedata, 'data': data })


@login_required
def membersdetail_view(request, id):

	member = get_object_or_404(Member.objects.filter(library = request.user.library, id=id))

	modalforms = {
		'memberedit_form' : MemberForm(request.POST or None, instance=member)
	}

	related_filters = {
		'library': request.user.library,
		'member_id': id 
	}

	pagedata, data = process_data (
		request=request,
		model=Member,
		id=id,
		related_model=Transaction,
		related_filters=related_filters,
		modalforms=modalforms,
		jsoninfo={'folder': 'members', 'file': 'membersdetail'}
	
	)

	notes = list(WalletTransacton.objects.filter(member_id=id).values('note'))

	return render(request, 'library/details.html', {**pagedata, 'data': data, 'notes': notes })


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
		try:
			member.delete()
		except ValidationError as err_msg:
			for msg in err_msg:
				messages.add_message(request, messages.ERROR, str(msg))
			return redirect('membersdetail', id=id) 
		messages.add_message(request, messages.SUCCESS, f"{member.full_name} was deleted Successfully.")
		return redirect('members') 
	messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that.")
	return redirect('membersdetail', id=id) 