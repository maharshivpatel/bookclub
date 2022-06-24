from django.shortcuts import render, redirect
from transactions.models import Transaction 
from bookclub.utils import get_cover_from_api, handle_data, handle_filters
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from transactions.forms import IssueBookForm, MoneyForm

@login_required
def transactions_view(request):

	page = {
		'title': 'Transactions',
		'buttons': [
			{
			'btn_text':'Add Money',
			'button_action': "openmodal",
			'modal_target': "addMoneyModal",
			'css_btn_type': 'success',
			},
			{
			'btn_text':'Issue Book',
			'button_action': "openmodal",
			'modal_target': "issueBookModal",
			'css_btn_type': 'primary',
			},
		]
	}

	fields = [
		{
			'field_name': 'id',
			'field_title': 'ID',
			'url_prefix': 'details',
			'html_attr': 'disabled',
		},
		{
			'field_name': 'member__full_name',
			'field_title': 'Members',
			'url_prefix': 'details',
			'html_attr': 'autofocus',
		},
		{
			'field_name': 'trans_amount',
			'field_title': 'Amount',
			'css_class': 'fw-bold currency-pn',
		},
		{
			'field_name': 'book__title',
			'field_title': 'Book',
		},
		{
			'field_name': 'is_return',
			'field_title': 'Is Return',
		},
		{
			'field_name': 'is_lost',
			'field_title': 'Is Lost',
		},
		{
			'field_name': 'issue_date',
			'field_title': 'Issue Date',
		},
		{
			'field_name': 'return_date',
			'field_title': 'Return Date',
		},
	]

	issuebook_initial = {
		'library': request.user.library,
		'created_by': request.user,
	}

	addmoney_initial = {
			'library': request.user.library,
			'created_by': request.user,
			'is_add_balance': True
			}
	
	try:
		issuebook_form = IssueBookForm(initial=issuebook_initial)
		addmoney_form = MoneyForm(initial=addmoney_initial)
	
	except ValidationError as err_msg:
		for msg in err_msg:
			messages.add_message(request, messages.ERROR, str(msg))
	
	create_transaction_modals = [
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
		{
			'modal_id': 'issueBookModal',
			'modal_title': 'Issue Book',
			'p_btn_txt': 'Issue',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			'submit_url_name': 'bookissue',		
			'form': issuebook_form,
		},
	]
	
	filters = handle_filters(request, fields)
	fieldlist = [ field['field_name'] for field in fields ]
	transactions = Transaction.objects.filter(library=request.user.library, **filters).values(*fieldlist)

	data = handle_data( fields, transactions)

	return render(request, 'library/list.html', {'page': page, 'fields': fields, 'data': data, 'modals': create_transaction_modals })


@login_required
def transactiondetail_view(request, id):

	page = {
		'title': 'Transaction Detail',
		'buttons': [
			{
				'btn_text':'back',
				'button_action': "redirect",
				'url_name': f'transactions',
				'css_btn_type': 'light',
			},
		]
	}


	fields = [
		{
			'field_name': 'id',
			'field_title': 'TRANS ID',
			'col_span': 2,
		},
		{
			'field_name': 'book__title',
			'field_title': 'Book Title',
			'col_span': 10,
		},
		{
			'field_name': 'member__full_name',
			'field_title': 'Members',
		},
		{
			'field_name': 'member__wallet__balance',
			'field_title': 'Member\'s Balance',
			'css_class': 'text-success currency-pn'
		},
		{
			'field_name': 'trans_amount',
			'field_title': 'Transaction Amount',
			'css_class': 'text-primary currency'
		},
		{
			'field_name': 'book__isbn10',
			'field_title': 'Book ISBN',
		},
		{
			'field_name': 'is_return',
			'field_title': 'Is Return',
		},
		{
			'field_name': 'is_lost',
			'field_title': 'Is Lost',
		},
		{
			'field_name': 'issue_date',
			'field_title': 'Issue Date',
		},
		{
			'field_name': 'return_date',
			'field_title': 'Return Date',
		},
		{
			'field_name': 'duration',
			'field_title': 'Duration',
		},
	]



	fieldlist = [ field['field_name'] for field in fields ]

	transaction = Transaction.objects.filter(library=request.user.library, id=id).values(*fieldlist)

	if transaction[0]['is_return'] or transaction[0]['is_lost']:
		page['buttons'].append(
			{
				'btn_text':'Delete',
				'button_action': 'post_form',
				'url_name': f'transactiondelete',
				'obj_url_id': id,
				'method': 'POST',
				'css_btn_type': 'danger',
			}
		)

	if not transaction[0]['is_return']:
		
		page['buttons'].append(
			{
				'btn_text':'Return',
				'button_action': "post_form",
				'url_name': 'bookreturn',
				'obj_url_id': id,
				'css_btn_type': 'success',
			}
		)

	if not transaction[0]['is_lost'] and not transaction[0]['is_return']:

		page['buttons'].append(
			{
				'btn_text':'Lost',
				'button_action': "post_form",
				'url_name': 'booklost',
				'obj_url_id': id,
				'css_btn_type': 'warning',
			}
		)

	data = handle_data( fields, transaction )

	isbn =  transaction[0]['book__isbn10']

	book_image_url = get_cover_from_api(
		f'http://covers.openlibrary.org/b/isbn/{isbn}-M.jpg'
		)


	return render(request, 'library/details.html', { 'data': data, 'book_image_url': book_image_url, 'page': page,})

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
	addmoney_initial = {
			'library': request.user.library,
			'created_by': request.user,
			'is_add_balance': True
		}

	if request.method == "POST":
		form = MoneyForm(request.POST or None, initial=addmoney_initial)

		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, f" Money Added ")
			return redirect('members')
	
		if form.is_bound:
			return render(request, 'library/page_edit.html', {'form': form})
	
	messages.add_message(request, messages.ERROR, "Woah, You visited add Transaction page! you shouldn't do that.")
	return redirect('members')


@login_required
def bookissue_view(request):

	if request.method == "GET":	
		messages.add_message(request, messages.ERROR, "Woah, You visited add Transaction page! you shouldn't do that.")
		return redirect('transactions')
	
	initial = {
		'library': request.user.library,
		'created_by': request.user,
	}

	if request.method == "POST":
		try:
			form = IssueBookForm(request.POST or None, initial=initial)

			if form.is_valid():
				form.save()
				messages.add_message(request, messages.SUCCESS, f"Book has Issued Successfully ")
				return redirect('transactions')
		
			if form.is_bound:
				return render(request, 'library/page_edit.html', {'form': form})
	
		except ValidationError as err_msg:
			for msg in err_msg:
				messages.add_message(request, messages.ERROR, str(msg))
	
	return redirect('transactions')

@login_required
def bookreturn_view(request, id):
	if request.method == 'POST':
		transaction = Transaction.objects.get(id=id, created_by__library = request.user.library)
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
		transaction = Transaction.objects.get(id=id, created_by__library = request.user.library)
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
		transaction = Transaction.objects.get(id=id, created_by__library = request.user.library)
		transaction.delete()
		messages.add_message(request, messages.SUCCESS, f"You deleted transaction with id {id}. ")
		return redirect('transactions') 
	messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that.")
	return redirect('transactiondetail', id=id) 