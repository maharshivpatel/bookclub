from django.shortcuts import render, redirect
from transactions.models import Transaction 
from bookclub.utils import get_cover_from_api, handle_data, handle_filters
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
	
	create_transaction_modals = [
		{
			'modal_id': 'addMoneyModal',
			'modal_title': 'Add Money',
			'p_btn_txt': 'Add',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			# 'form': 'django-form-variable-name',
		},
		{
			'modal_id': 'issueBookModal',
			'modal_title': 'Issue Book',
			'p_btn_txt': 'Issue',
			'p_btn_type': 'primary',
			's_btn_txt': 'Cancel',
			's_btn_type': 'secondary',
			# 'form': 'django-form-variable-name',
		},
	]
	
	filters = handle_filters(request, fields)
	fieldlist = [ field['field_name'] for field in fields ]
	transactions = Transaction.objects.filter(**filters).values(*fieldlist)

	data = handle_data( fields, transactions)

	return render(request, 'library/list.html', {'page': page, 'fields': fields, 'data': data, 'modals': create_transaction_modals })


@login_required
def transactiondetail_view(request, id):

	page = {
		'title': 'Transaction Detail',
		'buttons': []
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

	transaction = Transaction.objects.filter(created_by__library=request.user.library, id=id).values(*fieldlist)

	if not transaction[0]['is_return']:

		page['buttons'].append(
			{
				'btn_text':'back',
				'button_action': "redirect",
				'url_name': f'transactions',
				'css_btn_type': 'light',
			}
		)

		page['buttons'].append(
			{
				'btn_text':'Delete',
				'button_action': 'post_form',
				'url_name': f'transactiondelete',
				'obj_url_id': id,
				'method': 'POST',
				'css_btn_type': 'danger',
			},
		)

		page['buttons'].append(
			{
				'btn_text':'Return',
				'button_action': "post_form",
				'url_name': 'bookreturn',
				'obj_url_id': id,
				'css_btn_type': 'success',
			}
		)

	if not transaction[0]['is_lost']:

		page['buttons'].append(
			{
				'btn_text':'back',
				'button_action': "redirect",
				'url_name': f'transactions',
				'css_btn_type': 'light',
			}
		)

		page['buttons'].append(
			{
				'btn_text':'Delete',
				'button_action': 'post_form',
				'url_name': f'transactiondelete',
				'obj_url_id': id,
				'method': 'POST',
				'css_btn_type': 'danger',
			},
		)

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
def bookissue_view(request):
	if request.method == 'POST':
		messages.add_message(request, messages.SUCCESS, f"You have issued book")
		return redirect('transactions') 
	messages.add_message(request, messages.ERROR, "Woah, You visited issue book page! you shouldn't do that.")
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