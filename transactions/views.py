from django.shortcuts import render, redirect
from transactions.models import Transaction, WalletTransacton
from bookclub.utils import get_cover_from_api, process_data
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from transactions.forms import IssueBookForm, MoneyForm
from django.shortcuts import get_object_or_404

@login_required
def transactions_view(request):

	bookissue_initial = {
		'library': request.user.library,
		'created_by': request.user,
	}

	moneyadd_initial = {
			'library': request.user.library,
			'created_by': request.user,
			'is_add_balance': True
	}
	
	try:
		modalforms ={
			"bookissue_form" : IssueBookForm(initial=bookissue_initial),
			"moneyadd_form" : MoneyForm(initial=moneyadd_initial)
		}

	
	except ValidationError as err_msg:
		for msg in err_msg:
			messages.add_message(request, messages.ERROR, str(msg))
	


	pagedata, data = process_data (
		request=request,
		model=Transaction,
		modalforms=modalforms,
		jsoninfo={'folder': 'transactions', 'file': 'transactions'}
	
	)

	return render(request, 'library/list.html', {**pagedata, 'data': data })


@login_required
def transactiondetail_view(request, id):

	related_filters = {
		'transaction_id': id 
	}


	pagedata, data = process_data (
		request=request,
		model=Transaction,
		id=id,
		related_model=WalletTransacton,
		related_filters=related_filters,
		jsoninfo={'folder': 'transactions', 'file': 'transactiondetail'}
	)


	for field in data[0]:
		if field.get('name') == 'is_return':
			is_return = True if field.get('value') == "Yes" else False
		if field.get('name') == 'is_lost':
			is_lost = True if field.get('value') == "Yes" else False
		if field.get('name') == 'book__isbn10':
			isbn10 = field.get('value')


	if not is_return:
		
		pagedata['page']['buttons'].append(
			{
				'btn_text':'Return',
				'button_action': "post_form",
				'url_name': 'bookreturn',
				'obj_url_id': id,
				'css_btn_type': 'success',
			}
		)


	if not is_lost and not is_return:

		pagedata['page']['buttons'].append(
			{
				'btn_text':'Lost',
				'button_action': "post_form",
				'url_name': 'booklost',
				'obj_url_id': id,
				'css_btn_type': 'warning',
			}
		)

	if is_lost or is_return:
		pagedata['page']['buttons'].append(
			{
				'btn_text':'Delete',
				'button_action': 'post_form',
				'url_name': 'transactiondelete',
				'obj_url_id': id,
				'method': 'POST',
				'css_btn_type': 'danger',
			}
		)

	book_image_url = get_cover_from_api(
		f'http://covers.openlibrary.org/b/isbn/{isbn10}-M.jpg'
		)


	return render(request, 'library/details.html', {**pagedata, 'data': data, 'book_image_url': book_image_url})

@login_required
def transactiondelete_view(request, id):
	if request.method == 'POST':
		transaction = Transaction.objects.get(id=id, created_by__library = request.user.library)
		transaction.delete()
		messages.add_message(request, messages.SUCCESS, f"You deleted transaction with id {id}. ")
		return redirect('transactions') 
	messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that.")
	return redirect('transactiondetail', id=id) 


@login_required
def moneyadd_view(request):
	moneyadd_initial = {
			'library': request.user.library,
			'created_by': request.user,
			'is_add_balance': True
		}

	if request.method == "POST":
		moneyadd_form = MoneyForm(request.POST or None, initial=moneyadd_initial)

		if moneyadd_form.is_valid():
			moneyadd_form.save()
			messages.add_message(request, messages.SUCCESS, f" Money Added ")
			return redirect('members')
	
		if moneyadd_form.is_bound:
			return render(request, 'library/page_edit.html', {'form': moneyadd_form})
	
	messages.add_message(request, messages.ERROR, "Woah, You visited add Transaction page! you shouldn't do that.")
	return redirect('members')


@login_required
def bookissue_view(request):

	if request.method == "GET":	
		messages.add_message(request, messages.ERROR, "Woah, You visited Issue Book page! you shouldn't do that.")
		return redirect('transactions')
	
	bookissue_initial = {
		'library': request.user.library,
		'created_by': request.user,
	}

	if request.method == "POST":
		try:
			bookissue_form = IssueBookForm(request.POST or None, initial=bookissue_initial)

			if bookissue_form.is_valid():
				bookissue_form.save()
				messages.add_message(request, messages.SUCCESS, f"Book has Issued Successfully ")
				return redirect('transactions')
		
			if bookissue_form.is_bound:
				return render(request, 'library/page_edit.html', {'form': bookissue_form})
	
		except ValidationError as err_msg:
			for msg in err_msg:
				messages.add_message(request, messages.ERROR, str(msg))
	
	return redirect('transactions')

@login_required
def bookreturn_view(request, id):
	if request.method == 'POST':
		transaction = get_object_or_404(Transaction.objects.filter(id=id, created_by__library = request.user.library))
		transaction.is_return = True;
		transaction.is_lost = False;
		transaction.save()
		messages.add_message(request, messages.SUCCESS, f"{transaction.book.title} is Returned Successfully.")
		return redirect('transactiondetail', id=id) 
	messages.add_message(request, messages.ERROR, "Woah, You visited lost book page! you shouldn't do that.")
	return redirect('transactiondetail', id=id) 

@login_required
def booklost_view(request, id):
	if request.method == 'POST':
		transaction =  get_object_or_404(Transaction.objects.filter(id=id, created_by__library = request.user.library))
		transaction.is_return = False;
		transaction.is_lost = True;
		transaction.save()
		messages.add_message(request, messages.WARNING, f"{transaction.book.title} is marked as Lost.")
		return redirect('transactiondetail', id=id)
	messages.add_message(request, messages.ERROR, "Woah, You visited lost book page! you shouldn't do that.")
	return redirect('transactiondetail', id=id) 

@login_required
def transactiondelete_view(request, id):
	if request.method == 'POST':
		transaction =  get_object_or_404(Transaction.objects.filter(id=id, created_by__library = request.user.library))
		transaction.delete()
		messages.add_message(request, messages.SUCCESS, f"You deleted transaction with id {id}. ")
		return redirect('transactions') 
	messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that.")
	return redirect('transactiondetail', id=id) 