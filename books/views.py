import json, random
from django.shortcuts import get_object_or_404
from transactions.models import Transaction
from books.models import Book, Author, Publisher
from books.forms import BookForm
from django.core.exceptions import ValidationError
from bookclub.utils import load_json, process_data, handle_data, handle_filters, load_json, request_data_from_api, get_cover_from_api
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime


@login_required
def books_view(request):

	pagedata, data = process_data (
		request=request,
		model=Book,
		jsoninfo={'folder': 'books', 'file': 'books'}
	)

	return render(request, 'library/list.html', {**pagedata, 'data': data })


@login_required
def booksdetail_view(request, id):

	related_filters = {
		'library': request.user.library,
		'book_id': id,
	}
	
	pagedata, data = process_data (
		request=request,
		model=Book,
		id=id,
		related_model=Transaction,
		related_filters=related_filters,
		jsoninfo={'folder': 'books', 'file': 'booksdetail'}
	)
	
	isbn10 = Book.objects.get(id=id).isbn10

	book_image_url = get_cover_from_api(
		f'http://covers.openlibrary.org/b/isbn/{isbn10}-M.jpg'
		)

	return render(request, 'library/details.html', {**pagedata, 'book_image_url': book_image_url, 'data': data })


@login_required
def bookadd_view(request):

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
	
	pagedata = load_json(folder='books', file='bookadd')

	return render(request, 'library/add_edit.html', {**pagedata, 'form': form }) 


@login_required
def bookedit_view(request, id):
	
	book = get_object_or_404(Book.objects.filter(library=request.user.library, id=id))

	form = BookForm(request.POST or None, instance=book)

	if request.method == 'POST':

		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, f"{book.title} edited Successfully.")
			return redirect('bookdetail', id=id)
		
		elif form.is_bound:
			messages.add_message(request, messages.ERROR, f"Error while editing {book.title} ")
		
	pagedata, data = process_data (
		request=request,
		model=Book,
		id=id,
		jsoninfo={'folder': 'books', 'file': 'bookedit'}
	)

	return render(request, 'library/add_edit.html', {**pagedata, 'form': form }) 


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


@login_required
def booksimport_view(request):

	jsoninfo = {'folder': 'books', 'file': 'booksimport'}

	pagedata = load_json(**jsoninfo)
	fields = pagedata.get('fields', [])

	filters = handle_filters(request, fields, pagedata['extra_filters'], api=True)

	url = 'https://frappe.io/api/method/frappe-library'
	
	raw_data = request_data_from_api(url, 'GET', params=filters)

	data = raw_data.get('message', [])
	
	addedbooks = []


	list_data = handle_data( fields, data)

	unique_list_data = []
	
	for dlist in list_data:
	
		bookid = dlist[0]['value']
	
		if not bookid in addedbooks:
			addedbooks.append(bookid)
			unique_list_data.append(dlist)


	json_data = json.dumps(data)


	if request.method == 'POST':
	
		data = dict(request.POST)
		bookid = data.get('bookid')
		raw_json = data.get('raw_json')
		qty = data.get('qty')
		jsondata = json.loads(raw_json[0])
		
		mapped_id_qty = (
			[
				{ 
					'bookID' : i[1],
					'qty' : qty[i[0]],
				}
			for i in enumerate(bookid)
			if int(qty[i[0]]) > 0
			]
		) 
		
		ready_data = ([
				[
						{ **book, **jsonbook }
					for book in mapped_id_qty
					if	book['bookID'] == jsonbook['bookID']
				]
	  				for jsonbook in jsondata
				])

		for book in ready_data:
			
			if len(book) != 0:

				book = book[0]
				
				authors_list = book['authors'].split('/')
				publisher_list = book['publisher'].split('/')
				
				library = request.user.library
				
				if not library:
					return redirect('books')
				
				bookdata = {
					"bookid": book['bookID'],
					"authors_text": book['authors'],
					"publishers_text": book['publisher'],
					"library": library,
					"title": book['title'],
					"avg_rating": book['average_rating'],
					"isbn10": book['isbn'],
					"isbn13": book['isbn13'],
					"lang_code":book['language_code'],
					"pages_in_book": book['  num_pages'],
					"rating_num": book['ratings_count'],
					"publication_date": datetime.strptime(book['publication_date'], '%m/%d/%Y').date(),
					'rent_fee': random.randint(5,30), 
					"book_value": random.randint(100,300),
				}

				book_obj = Book.objects.filter(bookid=bookdata['bookid'], library_id=library.id).first()
				
				if not book_obj:
					book_obj = Book(**bookdata)

				book_obj.instock_qty += int(book['qty'])
				book_obj.save()

				for publisher in publisher_list:
					publisher_obj = Publisher.objects.filter(full_name=publisher, library_id=library.id).first()

					if not publisher_obj:
						publisher_obj = Publisher.objects.create(full_name=publisher, library=library)
						publisher_obj.save()
					
					book_obj.publishers.add(publisher_obj)

				for author in authors_list:
					author_obj = Author.objects.filter(full_name=author, library_id=library.id).first()
					
					if not author_obj:
						author_obj = Author.objects.create(full_name=author, library=library)
						author_obj.save()
					
					book_obj.authors.add(author_obj)
				
				book_obj.save()

	
	return render(request, 'library/list.html', {**pagedata, 'api': True, 'data': unique_list_data, 'raw_data': json_data })