from django.db import models
from django.contrib import admin
import datetime
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, UserManager
from django.forms import ValidationError
from . import settings


# Create your models here.

DURATION_ZERO = datetime.time(hour=0)
DEFAULT_DURATION = datetime.time(hour=1)
DEFAULT_TIME = datetime.time(hour=12)

phoneValidator = RegexValidator(
    regex=r'[0-9][0-9 ]+',
    message='Not a valid phone number')




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
        gender,
        notes,
        password=None
    ):
        """
        Creates and saves a Customer with the given particulars and password.
        """
        if not username:
            raise ValueError('Customers must have a username')

        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            date_of_birth=date_of_birth,
            gender=gender,
            notes=notes,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user



class Customer(User):
    """ Customer/Client/Patient details. 
    """

    # gender options
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    # title options
    MR = 'MR'
    MRS = 'MRS'
    MISS = 'MISS'
    MS = 'MS'
    DR = 'DR'
    PROF = 'PROF'
    REV = 'REV'
    TITLE_CHOICES = (
        (MR, 'Mr'),
        (MRS, 'Mrs'),
        (MISS, 'Miss'),
        (MS, 'Ms'),
        (DR, 'Dr'),
        (PROF, 'Prof'),
        (REV, 'Rev'),
    )


    class Meta(User.Meta):
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'


    objects = CustomerManager()

    title = models.CharField(
        max_length=4,
        choices=TITLE_CHOICES,
        default=MRS,
    )
    phone = models.CharField(
        max_length=20, 
        validators=[phoneValidator], 
        blank=True, 
        null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default=FEMALE,
    )
    notes = models.TextField(blank=True)


    def natural_key(self):
        """
        Serialisation aid. Not needed ATM.
        """
        return (self.username,)


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



class Resource(models.Model):
    """
    A finite bookable resource, such as a room or piece of equipment.
    
    TODO: May need to generalise this by adding ResourceType.
    """

    name = models.CharField(max_length=40)
    description = models.TextField(blank=True)


    def __str__(self):
        return '{0}'.format(self.name)



class Treatment(models.Model):
    """
    A treatment. 
    
    Treatments are characterised by the resource(s) they need, and 
    the minimum time duration.
    
    TODO: Currently the model assumes only one resource.
    """

    name = models.CharField(max_length=40)
    min_duration = models.DurationField(blank=True)
    resource_required = models.BooleanField(default=False)


    def __str__(self):
        return '{0}'.format(self.name)



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

    date = models.DateField(blank=False)
    time = models.TimeField(blank=False, default=DEFAULT_TIME)
    # kludge for duration enables using a time widget
#    duration = models.DurationField(blank=True, default=DEFAULT_DURATION)
    duration = models.TimeField(blank=True, default=DEFAULT_DURATION)

    notes = models.TextField(blank=True)
    creator = models.ForeignKey(
        User, 
        blank=True, 
        null=True, 
        related_name='created_entries'
    )
    created = models.DateTimeField(auto_now_add=True)

    editor = models.ForeignKey(
        User, 
        blank=True, 
        null=True, 
        related_name='edited_entries'
    )
    edited = models.DateTimeField(auto_now=True)

    customer = models.ForeignKey(
        Customer, 
        blank=True, 
        null=True, 
        related_name='entries',
    )
    treatment = models.ForeignKey(Treatment, blank=True, null=True)
    resource = models.ForeignKey(Resource, blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    no_show = models.BooleanField(default=False)


    def __str__(self):
        name = '{0}'.format(
            self.customer if self.customer 
            else self.creator
        )
        return ' - '.join(
            [name, ('{0}'.format(self.treatment) if self.treatment else '')]
        )


    def short(self):
        return ' - '.join([
                ('{0}'.format(self.resource) if self.resource else ''),
                ('{0}'.format(self.treatment) if self.treatment else ''),
                (self.notes if self.notes else ''),
            ]
        )


    def duration_delta(self):
        """
        Convert duration-as-time to duration-as-delta.
        """
        the_zero = datetime.datetime.combine(self.date, DURATION_ZERO)
        the_duration = datetime.datetime.combine(self.date, self.duration)
        return the_duration - the_zero


    def time_end(self):
        """
        Calculate the time of the end of the entry from the start time and the
        duration.
        Sadly the naive method of adding the duration directly to the time 
        is not supported in python datetime arithmetic; a datetime object has 
        to be used.
        """
        the_time = datetime.datetime.combine(self.date, self.time)
        the_time_end = the_time + self.duration_delta()
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


    def validateResourceRequirement(self):
        """
        Context validation of resource requirements.
        
        If a treatment requires a resource, a resource must be specified.
        """
        if self.treatment and self.treatment.resource_required:
            if not self.resource:
                raise ValidationError(
                    'Resource requirement is not met.'
                )


    def validateDuration(self):
        """
        Context validation of duration.
        
        Duration may be invalid if it is smaller than the minimum for the
        treatment.
        """
        if self.treatment and self.treatment.min_duration:
            if (
                not self.duration 
                or self.treatment.min_duration > self.duration_delta()
            ):
                raise ValidationError(
                    'Duration must be at least the minimum treament time.'
                )


    def validateNoResourceConflicts(self):
        """
        Context validation of date, time, duration and resource.
        
        The entry is invalid if it clashes in time and resource with
        a pre-existing entry. Cancelled entries don't count.
        """
        if self.cancelled or self.no_show:
            return

        if self.resource:

            # get the day's uncancelled entries sharing the same resource
            savedEntries = Entry.objects.filter(
                date=self.date, 
                resource=self.resource,
                cancelled=False,
                no_show=False,
            )

            # ensure no time clashes
            for other in savedEntries:
                if self == other:
                    # if we are just saving the same entry, its OK
                    if not self.pk or (self.pk and self.pk != other.pk):
                        raise ValidationError(
    'Resource clash with another Entry. Please change resource or time.'
                        )


    def validateCustomerNotDoubleBooked(self):
        """
        Context validation of customer.
        
        A named customer cannot have two entries at the same time, irrespective
        of other resource criteria. Cancelled entries don't count.
        """
        if self.cancelled or self.no_show:
            return

        if self.customer:

            # get any uncancelled entries for the same customer on the same day
            savedEntries = Entry.objects.filter(
                date=self.date, 
                customer=self.customer,
                cancelled=False,
                no_show=False,
            )

            # ensure no time clashes
            for other in savedEntries:
                if self == other:
                    # if we are just saving the same entry, its OK
                    if not self.pk or (self.pk and self.pk != other.pk):
                        raise ValidationError(
    'Double booking is not allowed. Please choose another time.'
                        )


    def validateTradingHours(self):
        """
        Context validation of trading times.
        
        Staff members may add/edit an entry at any time subject to other 
        business rules. Customers may only add/edit entries consistent with
        opening hours.
        """
        if not self.editor.is_staff:
            dow = self.date.weekday()
            if not (
                self.time >= settings.DIARY_OPENING_TIMES[dow] and 
                self.time_end() <= settings.DIARY_CLOSING_TIMES[dow]
            ):
                raise ValidationError(
                    'Sorry, the store is closed then. Try changing the time.'
                )


    def validateFuture(self):
        """
        Ensure customers cannot book times in the past or in the advance booking
        period.
        
        Staff can book entries whenever they like, but customers can only book
        times in the future.
        """
        if not self.editor.is_staff:
            tz_now = timezone.localtime(timezone.now())
            now = datetime.datetime(
                tz_now.year, tz_now.month, tz_now.day,
                tz_now.hour, tz_now.minute, tz_now.second,
            )
            advance_booking_date = (
                datetime.datetime(
                    tz_now.year, tz_now.month, tz_now.day, 0, 0, 0,
                ) + 
                datetime.timedelta(days=settings.DIARY_MIN_BOOKING)
            )
            bookedTime = datetime.datetime.combine(self.date, self.time)
            if bookedTime < now:
                raise ValidationError(
                    'Please book a date/time in the future.'
                )
            if bookedTime < advance_booking_date:
                raise ValidationError(
                    'Need to book ahead.'
                )


    def clean(self, *args, **kwargs):
        """
        Override Model method to validate the content in context. 
        
        This applies the business rules of the Entry validateX methods.
        """
        self.validateResourceRequirement()
        self.validateDuration()
        self.validateNoResourceConflicts()
        self.validateCustomerNotDoubleBooked()
        self.validateTradingHours()
        self.validateFuture()

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

