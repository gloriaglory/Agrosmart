from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds fields for phone number and ID number.
    A user with an ID number is considered a seller, otherwise a buyer.
    """
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    id_number = models.CharField(_('ID number'), max_length=50, blank=True, null=True)

    @property
    def is_seller(self):
        """
        Determines if the user is a seller based on whether they have an ID number.
        Returns True if the user has an ID number, False otherwise.
        """
        return bool(self.id_number)

    @property
    def role(self):
        """
        Returns the user's role as a string.
        'seller' if the user has an ID number, 'buyer' otherwise.
        """
        return 'seller' if self.is_seller else 'buyer'
