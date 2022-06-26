from django.contrib import messages
from decimal import Decimal
from datetime import datetime, timedelta
from humanize import precisedelta, naturaldate
from django.utils.timezone import make_aware
import requests as rq
import parsedatetime


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