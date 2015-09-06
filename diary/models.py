from django.db import models
from django.contrib import admin
import datetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, UserManager
from django.forms import ValidationError


# Create your models here.

DURATION_ZERO = datetime.time(hour=0)
DEFAULT_DURATION = datetime.time(hour=1)
DEFAULT_TIME = datetime.time(hour=12)

phoneValidator = RegexValidator(
    regex=r'[0-9][0-9 ]+',
    message='Not a valid phone number')




class Entry(models.Model):
    """
    A diary entry, some event entered in the calendar.

    Entries need to be able to compare times and do basic temporal arithmetic.
    To do this (I think) we need to implement rich comparator methods so one
    entry knows how to compare itself with another.
    One possible (potentially undesirable) side-effect is that entries may
    consider each other 'equal' when they have neither the same start time
    nor the same duration. They will nevertheless be 'equivalent' in sharing
    a portion of time.
    """

    title = models.CharField(max_length=40)
    snippet = models.CharField(max_length=150, blank=True)
    body = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateField(blank=True)
    time = models.TimeField(blank=True, default=DEFAULT_TIME)
    # kludge for duration enables using a time widget
#    duration = models.DurationField(blank=True, default=DEFAULT_DURATION)
    duration = models.TimeField(blank=True, default=DEFAULT_DURATION)
    creator = models.ForeignKey(User, blank=True, null=True)
    remind = models.BooleanField(default=False)


    def __str__(self):
        if self.title:
            return self.creator.username + ' - ' + self.title
        else:
            return self.creator.username + ' - ' + self.snippet[:40]


    def short(self):
        if self.snippet:
            return '<i>{0}</i> - {1}'.format(self.title, self.snippet)
        else:
            return self.title
    short.allow_tags = True


    def time_end(self):
        """
        Calculate the time of the end of the entry from the start time and the
        duration.
        Sadly the naive method of adding the duration directly to the time 
        is not supported in python datetime arithmetic; a datetime object has 
        to be used.
        """
        the_time = datetime.datetime.combine(self.date, self.time)
        the_zero = datetime.datetime.combine(self.date, DURATION_ZERO)
        the_duration = datetime.datetime.combine(self.date, self.duration)
        duration_delta = the_duration - the_zero
        the_time_end = the_time + duration_delta
        return the_time_end.time()


    def __eq__(self, other):
        """
        Determine if the entries are 'eqivalent' (not necessarily mathematically
        equal).
        NOTE: time period end time is non-inclusive.
        """
        # dates must be equal to start with
        # TODO: note time rounding kludge
        if (self.date.timetuple()[0:3] != other.date.timetuple()[0:3]):
            return False

        # time periods do not overlap; self happens before other
        if (self.time < other.time and self.time_end() <= other.time):
            return False

        # time periods do not overlap; self happens after other
        if (self.time > other.time and self.time >= other.time_end()):
            return False

        # anything else has to mean they overlap in time, right?
        return True


    def clean(self, *args, **kwargs):
        """
        Override Model method to validate the content. We need the entry to be 
        invalid if it clashes in time with a pre-existing entry.
        """
        # get the day's existing entries
        savedEntries = Entry.objects.filter(date=self.date)

        # ensure no time clashes
        for other in savedEntries:
            if self == other:
                # if we are just saving the same entry to the same time, its OK
                if not self.pk or (self.pk and self.pk != other.pk):
                    raise ValidationError(
            'Time clash not allowed. Please change the date/time/duration.'
                    )
        # now do the standard field validation
        super(Entry, self).clean(*args, **kwargs)


    def save(self, *args, **kwargs):
        """
        Override the parent method to ensure custom validation in clean() is 
        done.
        """
        self.full_clean()
        super(Entry, self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural = 'entries'



class CustomerManager(UserManager):


    def get_by_natural_key(self, username):
        """
        Enable serialisation without pk. Not needed ATM.
        """
        return self.get(username=username)


    def create_user(self, 
        username, 
        first_name, 
        last_name, 
        email, 
        phone, 
        date_of_birth, 
        password=None
    ):
        """
        Creates and saves a Customer with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Customers must have a username')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user



class Customer(User):
    """ Customer/Client/Patient details. 
    """


    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    objects = CustomerManager()

    phone = models.CharField(
        max_length=20, 
        validators=[phoneValidator], 
        blank=True, 
        null=True)
    date_of_birth = models.DateField(blank=True, null=True)


    def natural_key(self):
        """
        Serialisation aid. Not needed ATM.
        """
        return (self.first_name,)


    def age(self):
        """
        Age to the nearest year.
        """
        if self.date_of_birth:
            now = timezone.now()
            return now.year - self.date_of_birth.year
        return None


    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

