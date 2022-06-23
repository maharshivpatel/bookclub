from django.db import models
from django.contrib.auth.models import AbstractUser

# Main model that represents Library and all other models will connect.
class Library(models.Model):

    name = models.CharField('Library Name', max_length=35, unique=True)
    books_instock = models.PositiveIntegerField('Books InStock', default=0)
    books_rented_out = models.PositiveIntegerField('Books Rented Out', default=0)
    max_book = models.PositiveSmallIntegerField('Maximum Books Person can Rent', default=3)
    max_debt_allowed = models.PositiveSmallIntegerField('Maximum Debt allowed', default=500)

    def __str__(self):
        return self.name


# Custom User Model that inherits from django user for Future Proofing.
class Librarian(AbstractUser):
    profile_pic = models.ImageField('Librarian\'s Profile Picture', upload_to = "librarian_pics/", blank=True, null=True)
    library = models.ForeignKey(Library, related_name='librarian', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if not self.first_name:
            return str(self.username)
        return str(' '.join((self.first_name, self.last_name)))

class Person(models.Model):
    full_name = models.CharField('Full Name', max_length=60)
    email = models.EmailField('Email', null=True, blank=True)
    
    class Meta:
        abstract = True