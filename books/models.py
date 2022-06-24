from django.db import models
from django.core.exceptions import ValidationError
from library.models import Person
from library.models import Library

import re
# isbn_validator taken from https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s13.html
# Python example, with checksum validation modified to throw error as per django field validation

def isbn_validator(isbn):
    
    # Checks for ISBN-10 or ISBN-13 format
    regex = re.compile('^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$')
    
    if regex.search(isbn):
        # Remove non ISBN digits, then split into a list
        chars = list(re.sub("[- ]|^ISBN(?:-1[03])?:?", "", isbn))
        # Remove the final ISBN digit from `chars`, and assign it to `last`
        last = chars.pop()
    
        if len(chars) == 9:
            # Compute the ISBN-10 check digit
            val = sum((x + 2) * int(y) for x,y in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:
            # Compute the ISBN-13 check digit
            val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"
    
        if (str(check) != last):
            raise ValidationError('%(isbn)s has Invalid ISBN check digit.', params={'isbn': isbn},)
    else:
        raise ValidationError('%(isbn)s is Invalid ISBN.', params={'isbn': isbn},)


class Author(Person):
    library = models.ForeignKey(Library, related_name='author', blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Publisher(Person):
    library = models.ForeignKey(Library, related_name='publisher', blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Book(models.Model):
    bookid = models.PositiveIntegerField('Book ID')
    title = models.CharField('Book Title', max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    isbn10 = models.CharField('ISBN 10', max_length=10, validators=[isbn_validator], blank=True, null=True)
    isbn13 = models.CharField('ISBN 13', max_length=13, validators=[isbn_validator], blank=True, null=True)
    lang_code = models.CharField('Language Code', max_length=15)
    publication_date = models.DateField()
    authors = models.ManyToManyField(Author)
    authors_text = models.CharField('Authors Name', max_length=250, editable=False)
    publishers = models.ManyToManyField(Publisher)
    publishers_text = models.CharField('Publishers Name', max_length=250, editable=False)
    avg_rating = models.DecimalField('Average Rating',  max_digits=6, decimal_places=2)
    rating_num = models.PositiveIntegerField('No of Reviews Received')
    instock_qty = models.PositiveSmallIntegerField('InStock Qty', default=0, editable=False)
    rented_out_qty = models.PositiveSmallIntegerField('Rented Out Qty', default=0, editable=False)
    lost_qty = models.PositiveSmallIntegerField('Lost Qty', default=0, editable=False)
    rent_fee = models.DecimalField('Rent Fee', max_digits=6, decimal_places=2, default=0)
    book_value = models.DecimalField( max_digits=6, decimal_places=2, null=True)
    pages_in_book = models.PositiveSmallIntegerField('Pages in Book', null=True)
    library = models.ForeignKey(Library, related_name='book', on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # store initial values to avoid unneccesary database calls
            self.m2m_changed_save = False
            self.initial_instock_qty = self.instock_qty

    def __str__(self):
        return self.title