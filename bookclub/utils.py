from django.contrib import messages
from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import redirect
from humanize import precisedelta, naturaldate
from django.utils.timezone import make_aware
import requests as rq
import parsedatetime
import os, json
from django.core.paginator import Paginator

def load_json(folder, file):
	current_folder = os.getcwd()
	file_path = os.path.join(current_folder, folder, 'data', f'{file}.json')
	open_file = open(file_path)
	pagedata = json.load(open_file)
	return pagedata


def handle_filters(request, fields, extra_filters=False, api=False):

	filters = {}

	def process_filters(list):
		msg =  "Filtered result for " 
		filterfields = []
		
		for params in list:

			field_name = params['field_name']
			field_title = params['field_title']
			field_value = request.GET.get(field_name, False)

			if field_value:
				if api:
					filters[field_name] =	request.GET.get(field_name)
				
				else:
					if field_name.endswith('_date'):

						if field_value and field_value.lower() == "not available":
							filters[f'{field_name}__isnull'] = True
						
						else:
							cal = parsedatetime.Calendar()
							time_struct, parse_status = cal.parse(field_value)
							date_filter = make_aware(datetime(*time_struct[:3]))

							if parse_status:
								filters[f'{field_name}__day'] =	date_filter.day
							else:
								messages.add_message(request, messages.ERROR, "Incorrect Date Provided");
					
					else:
						
						if field_name.startswith('is_'):
							if	field_value.lower()  == "no":
								field_value = False
							elif	field_value.lower() == "yes":
								field_value = True
							else:
								messages.add_message(request, messages.ERROR, "Please Provide value in Yes or No");
					
						filters[f'{field_name}__icontains'] =	field_value
				
				params['field_value'] = request.GET.get(field_name)
				
				filterfields.append(str(f'{field_title}: ' + request.GET.get(field_name)))
		
		if len(filterfields) != 0 :
			msg += ', '.join(filterfields)
			messages.add_message(request, messages.SUCCESS, msg);
		
		return filterfields


	if extra_filters: process_filters(extra_filters);

	process_filters(fields);
	
	return filters


def handle_data(fields, obj):

	data = obj

	ready_data = (
		[
		[
				{
					'value':
					
					"Not Available"
					
					if	datalist[x['field_name']] is None

					else	str(naturaldate(datalist[x['field_name']]))
					
					if		isinstance(datalist[x['field_name']], datetime )

					else	str(
								precisedelta(
									datalist[x['field_name']],
									minimum_unit='minutes',
									format="%0.0f"
								)
						)
					
					
					if		isinstance(datalist[x['field_name']], timedelta )
					
					else	'₹ ' + str(datalist[x['field_name']])

					if		isinstance(datalist[x['field_name']], Decimal)
					and		"currency" in str(x.get('css_class', False))

					else	datalist[x['field_name']]
					
					if		not isinstance(datalist[x['field_name']], bool)

					else	"Yes"
					
					if		datalist[x['field_name']]

					else	"No",

					'name': x['field_name'],

					'title': x['field_title'],

					'html_attr': x.get('html_attr', False),

					'css_class': x.get('css_class', False),
					
					'col_span': x.get('col_span', False),

					'url_prefix': False

							if not	x.get('url_prefix', False)
					
							else	str(x.get('url_prefix', False))
							
							+ '/'   +   str(datalist.get('id', '')),
				
				}
			for x in fields
			if	x['field_name'] in datalist
		
		]
			for datalist in data
		]
	)

	return ready_data


def handle_related_data(related_model, related_filters: dict, fields: list[str], header: list[str]):

	filtered_obj = related_model.objects.filter(**related_filters).values_list(*fields)

	
	ready_body_data = [
			[	
				"Not Available"
				if	field is None

				else	"Yes"
				if	isinstance(field, bool)
				and field

				else "No"
				if	isinstance(field, bool)
				and  not	field

				else	str(naturaldate(field))
				if	isinstance(field, datetime)
				
				else	'₹ ' + str(field)
				if isinstance(field, Decimal)
				
				else	str(field)
				
				for field in trans
			]

		for trans in filtered_obj
		]
	table = {
				'header': header,
				'body': ready_body_data
			}
	return table


def process_data(jsoninfo, request, model, id=False, related_model=False, related_filters=False, modalforms=False):

	pagedata = load_json(**jsoninfo)

	fields = pagedata.get('fields', [])
	related_table = []

	
	if modalforms:
		for modal in pagedata.get('modals', []):
			modal['form'] = modalforms.get(modal['form'])

	if id:
		for button in pagedata['page'].get('buttons', []):
			if button.get('obj_url_id', False):
				button['obj_url_id'] = id
			
		for modal in pagedata.get('modals', []):
			if modal.get('obj_url_id', False):
				modal['obj_url_id'] = id

		for related in pagedata.get('related_table', []):
			
			related_table.append(

				handle_related_data (
					related_model,
					related_filters,
					**related
					)
				)
		
		pagedata['related_table'] = related_table
			
		
		filters = {'id': id }

	else:
		filters = handle_filters(request, fields)
	
	fieldlist = [ field['field_name'] for field in fields ]

	obj = model.objects.filter(library=request.user.library, **filters).values(*fieldlist)

	page_obj, pagination = handle_paginaton(request, obj)

	data = handle_data( fields, page_obj)

	pagedata['pagination'] = pagination

	return pagedata, data


def handle_paginaton(request, obj):

	pages = Paginator(obj, 10)

	page_number = request.GET.get('page_number', 1)

	page_obj = pages.get_page(page_number)

	prevpage = False
	nextpage = False

	if page_obj.has_previous():
		prevpage = page_obj.previous_page_number()
	
	if page_obj.has_next():
		nextpage = page_obj.next_page_number()
	
	pagination = {
		"prevpage":prevpage,
		"currentpage": page_number,
		"nextpage": nextpage,
	}

	return page_obj, pagination


def get_cover_from_api(url: str):
	url = url
	response = rq.request('GET', url, params={})
	return response.request.url


def request_data_from_api(url: str, reqtype: str, params: list[dict]):
	url = url
	reqtype = reqtype
	response = rq.request(reqtype, url, params=params)
	data = {}
	try:
		data = response.json()
	except:
		pass
	return data