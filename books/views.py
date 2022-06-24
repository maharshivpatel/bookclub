from django.shortcuts import get_object_or_404
from books.models import Book
from books.forms import BookForm
from django.core.exceptions import ValidationError
from bookclub.utils import handle_data, handle_filters
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from bookclub.utils import get_cover_from_api

@login_required
def books_view(request):
	page = {
		'title': 'Books',
		'buttons': [
			{
				'btn_text':'Add Book',
				'url_name': 'bookadd',
				'button_action': "redirect",
				'css_btn_type': 'primary',
			}
		]
	}

	fields = [
		{
			'field_name': 'title',
			'field_title': 'Title',
			'url_prefix': 'details',
			'html_attr': 'autofocus',
		},
		{
			'field_name': 'authors_text',
			'field_title': 'Authors',
		},
		{
			'field_name': 'publishers_text',
			'field_title': 'Publishers',
		},
		{
			'field_name': 'isbn10',
			'field_title': 'ISBN',
		},
		{
			'field_name': 'instock_qty',
			'field_title': 'InStock',
			'css_class': 'text-primary fw-bold'
		},
		{
			'field_name': 'rented_out_qty',
			'field_title': 'Rented',
			'css_class': 'text-success fw-bold'
		},
	]


	filters = handle_filters(request, fields)
	books = Book.objects.filter(library=request.user.library, **filters).values()

	data = handle_data(fields, books)


	return render(request, 'library/list.html', { 'page': page, 'fields': fields, 'data': data })


@login_required
def booksdetail_view(request, id):
	page = {
		'title': 'Book Detail',
		'buttons': [
			{
			'btn_text':'View Books',
			'button_action': "redirect",
			'url_name': 'books',
			'css_btn_type': 'link',
			},
			{
			'btn_text':'Delete',
			'button_action': 'post_form',
			'url_name': 'bookdelete',
			'obj_url_id': id,
			'css_btn_type': 'danger',
			},
			{
			'btn_text':'Edit',
			'button_action': "redirect",
			'url_name': 'bookedit',
			'obj_url_id': id,
			'css_btn_type': 'primary',
			}
		]
	}

	fields = [
		{
			'field_name': 'bookid',
			'field_title': 'BookID',
			'col_span': 2,
		},
		{
			'field_name': 'title',
			'field_title': 'Title',
			'link': 'detail',
			'htmlattr': 'autofocus',
			'col_span': 10,
		},
		{
			'field_name': 'authors_text',
			'field_title': 'Authors',
			'col_span': 6,
		},
		{
			'field_name': 'publishers_text',
			'field_title': 'Publishers',
			'col_span': 6
		},
		{
			'field_name': 'isbn10',
			'field_title': 'ISBN',
		},
		{
			'field_name': 'publication_date',
			'field_title': 'Publication Date',
			'css_class': ''
		},
		{
			'field_name': 'avg_rating',
			'field_title': 'Avg Rating',
			'css_class': ''
		},
		{
			'field_name': 'instock_qty',
			'field_title': 'InStock',
			'css_class': 'text-primary'
		},
		{
			'field_name': 'rented_out_qty',
			'field_title': 'Rented',
			'css_class': 'text-success'
		},
		{
			'field_name': 'lost_qty',
			'field_title': 'Lost',
			'css_class': 'text-danger'
		},
		{
			'field_name': 'rent_fee',
			'field_title': 'Daily Rent Fee',
			'css_class': 'currency'
		},
		{
			'field_name': 'book_value',
			'field_title': 'Book Value',
			'css_class': 'currency'
		},
		{
			'field_name': 'pages_in_book',
			'field_title': 'Pages in Book',
		},
	]

	list_of_fields = [ field['field_name'] for field in fields ]
	book = Book.objects.filter(library=request.user.library, id=id).values(*list_of_fields)
	
	if len(book) == 0:
		messages.add_message(request, messages.WARNING, f"Detail Page for this book doesn't exist or you don't have access to it.")
		return redirect('books')

	isbn =  book[0]['isbn10']
	book_image_url = get_cover_from_api(
		f'http://covers.openlibrary.org/b/isbn/{isbn}-M.jpg'
		)

	data = handle_data(fields, book)


	return render(request, 'library/details.html', {'page': page, 'fields': fields, 'book_image_url': book_image_url, 'data': data })


@login_required
def bookadd_view(request):
	page = {
		'title': 'Add Book',
		'buttons': [
			{
			'btn_text':'Cancel',
			'url_name': 'books',
			'button_action': "redirect",
			'css_btn_type': 'secondary',
			},
			{
			'btn_text':'Save',
			'button_action': "submit",
			'css_btn_type': 'primary',
			}
		]
	}

	initial = {
		'library': request.user.library,
		}
	form = BookForm(initial=initial)

	if request.method == "POST":
	
		form = BookForm(request.POST or None, initial=initial)
		form.created_by = request.user
		form.library = request.user.library
	
		if form.is_valid():
			form.save()
			return redirect('books')

	return render(request, 'library/add_edit.html', { 'page': page, 'form': form  }) 


@login_required
def bookedit_view(request, id):
	page = {
		'title': 'Book Detail',
		'buttons': [
			{
			'btn_text':'Cancel',
			'button_action': "redirect",
			'url_name': 'bookdetail',
			'obj_url_id': id,
			'css_btn_type': 'secondary',
			},
			{
			'btn_text':'Update',
			'button_action': "submit",
			'css_btn_type': 'primary',
			}
		]
	}
	
	book = get_object_or_404(Book.objects.filter(library=request.user.library, id=id))

	form = BookForm(request.POST or None, instance=book)

	if request.method == 'POST':

		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, f"{book.title} edited Successfully.")
			return redirect('bookdetail', id=id)
		
		elif form.is_bound:
			messages.add_message(request, messages.ERROR, f"Error while editing {book.title} ")

	return render(request, 'library/add_edit.html', { 'page': page, 'form': form }) 


@login_required
def bookdelete_view(request, id):
	try:
		if request.method == 'POST':
			book = get_object_or_404(Book.objects.filter(library=request.user.library, id=id))
			book.delete()
			messages.add_message(request, messages.SUCCESS, f"{book.title} was deleted Successfully.")
			return redirect('books') 
		messages.add_message(request, messages.ERROR, "Woah, You visited delete page! you shouldn't do that. ")
		return redirect('bookdetail', id=id)
	except ValidationError as err_msg:
		for msg in err_msg:
			messages.add_message(request, messages.ERROR, str(msg))
	return redirect('bookdetail', id=id)