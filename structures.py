# Guest Flow Structure
guest_structure = {
    # primary button text ( action=form submit )
    'p_btn_txt': 'Create',
    # Secondary button Text
    's_btn_txt': 'select library',
    # Secondary button (action) url name of different view
    's_url_name': 'libraryselect'
    }


# Main Page Data Structure
page_structure = {

	'title': 'Title of Page',
    
    # Add buttons on title saction
	'buttons': [
		{
		'btn_text':'Button Text',
        # actions : redirect, submit, post_form, openmodal
		'button_action': "redirect",
        # modal id to show hidden modal
        'modal_target': 'createModal',
        # name of url from urls.py if type is redirect (required if redirect)
		'url_name': f'bookadd',
        # id of object to use for edit page. 
		'obj_url_id': 11,
        # all button styles from bootstrap 5. name excluding btn-
		'css_btn_type': 'primary',
		}
	]
}

# List of Fields to use in View.
fields_structure = [
		{
			'field_name': 'name of field defined in models.py for given model',
			# optional default will be used if not provided
            'field_title': 'Title to Display to Page',
            # optional providing will make url with parameter of that particular objects id.
			'url_prefix': 'detail',
             # optional providing will make that field focus if used in form / Input Field (Filters)
			'html_attr': 'autofocus',
            # any css class can be add to that paricular field.
			'css_class': 'text-primary fw-bold', # currency for currency fields.
            # Bootsrap col-4,8,12 class to modify look of details page.
            'col_span': 8,
		},
]

# modal form structure
modal_form_structure = [
    {
      # used to popup the hidden form
      'modal_id': 'createModal',
      # Title of Modal
      'modal_title': 'Title of Modal',

      'p_btn_txt': 'Primary Button',
      # all button styles from bootstrap 5. name excluding btn-
      'p_btn_type': 'primary',
      
      's_btn_txt': 'Secondary Button',
      # all button styles from bootstrap 5. name excluding btn-
      's_btn_type': 'secondary',
      # url name to which primary btn should submit
      'submit_url_name': ' urlname',
      # incase of edit form you can povide id as well
      'obj_url_id': id,
      # django form instance name 
      'form': 'django-form-variable-name',
    },
]
