from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Adds fields for phone number and ID number.
    A user with a NIDA number is considered a seller, otherwise a buyer.
    """
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    # NIDA number, stored as digits only. Required for sellers.
    id_number = models.CharField(_('NIDA number'), max_length=50, blank=True, null=True, unique=True)
    # Set once the NIDA number has been confirmed with the NIDA service.
    nida_verified = models.BooleanField(_('NIDA verified'), default=False)

    def save(self, *args, **kwargs):
        # Store blanks as NULL so the unique constraint allows many users without a NIDA number.
        if not self.id_number:
            self.id_number = None
        super().save(*args, **kwargs)

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
