from django.db import models
from library.models import Person
from library.models import Library
from phonenumber_field.modelfields import PhoneNumberField

class Member(Person):
    first_name = models.CharField('First Name', max_length=35)
    last_name = models.CharField('Last Name', max_length=35)
    library = models.ForeignKey(Library, verbose_name="Library", related_name='member', on_delete=models.CASCADE)
    phone_number = PhoneNumberField()

    def __str__(self):
        return self.full_name or str(self.first_name + ' ' + self.last_name)

class Wallet(models.Model):
    member = models.OneToOneField(Member, related_name='wallet', editable=False, on_delete=models.CASCADE)
    balance = models.DecimalField( max_digits=6, decimal_places=2, editable=False, default=0.00)

    def __str__(self):
         return ' | '.join((self.member.full_name, str(self.balance)))