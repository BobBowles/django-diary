from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
import datetime
from django.forms import ValidationError
import traceback
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings as main_settings
from . import settings
from . import views
import importlib as imp         # since Python 3.4
from freezegun import freeze_time


# Create your tests here.

from .models import Customer, Treatment, Resource, Entry
from django.contrib.auth.models import User


TIME_ZERO = datetime.time(0,0)


def yearsago(years, from_date=None):
    """
    Workaround for datetime.timedelta not knowing how to calculate leap years.
    Adapted from:
    http://stackoverflow.com/questions/765797/python-timedelta-in-years
    """
    if from_date is None:
        from_date = timezone.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)



class CustomerTests(TestCase):


    def test_customer_age(self):
        """
        Make sure the customer age calculation works correctly and as expected.
        """
        tenYearsAgo = yearsago(10)
        tenYearCustomer = Customer.objects.create(
            username='Ten',
            password='random',
            date_of_birth=tenYearsAgo,
        )
        self.assertEqual(tenYearCustomer.age(), 10)


    def test_customer_age_date_of_birth_not_set(self):
        """
        Make sure something sensible happens when we calculate age from an 
        undefined birth date.
        """
        undefinedBirthCustomer = Customer.objects.create(
            username='Ageless',
            password='random',
        )
        self.assertIsNone(undefinedBirthCustomer.age())



def create_customer(username):
    """
    Utility to generate a customer
    """
    customer = Customer.objects.create_user(
        username,                                   # username
        username,                                   # first_name
        username,                                   # last_name
        username+'@example.com',                    # email
        '123456',                                   # phone
        datetime.date(year=1950, month=6, day=1),   # d-o-b
        'M',                                        # gender
        'test user',                                # notes
    )
    customer.save()
    return customer


def obtain_superuser():
    """
    Utility to create a power user in the test database
    """
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        superuser = User.objects.create_superuser(
            'admin', 
            'admin@example.com', 
            'password'
        )
        superuser.save()
    return superuser


def create_treatment(name, min_duration, resource_required):
    """
    Utility to create a treatment.
    """
    treatment = Treatment(
        name=name, 
        min_duration=min_duration, 
        resource_required=resource_required,
    )
    treatment.save()
    return treatment


def create_resource(name, description):
    """
    Utility to make a resource
    """
    resource = Resource(
        name=name, 
        description=description,
    )
    resource.save()
    return resource


def change_time(date, time, delta):
    """
    Utility to change a time by a preset amount described by a delta.
    The date is just a tool.
    """
    return (datetime.datetime.combine(date, time) + delta).time()


def create_entry(dateDelta, time, duration, notes):
    """
    Utility to create an entry for testing.
    Updated to use timefield for duration.
    Updated to add a power user as default creator.
    Updated to add a power user as default editor.
    """
    date = timezone.datetime.today() + dateDelta
    duration_as_time = change_time(date, TIME_ZERO, duration)
    entry = Entry(
        notes=notes,
        date=date,
        time=time,
        duration=duration_as_time, # duration in the database is really a time
    )
    entry.creator = obtain_superuser()
    entry.editor = obtain_superuser()
    return entry


class EntryModelTests(TestCase):
    """
    Tests of the entry model methods. 
    These tests are primarily about making sure entries can do basic time
    arithmetic and comparisons, with the intention that they can determine time
    collisions.
    """


    def test_time_end_calculation(self):
        """
        Make sure the time arithmetic works as expected.
        """
        dateDelta = datetime.timedelta(days=0)
        time = datetime.time(hour=12)
        duration = datetime.timedelta(hours=1)
        entry = create_entry(
            dateDelta, 
            time,
            duration,
            'time calc test 1',
        )
        result = datetime.time(hour=13)
        self.assertEqual(entry.time_end(), result)


    def test_entry_treatment_resource_required(self):
        """
        If the entry has a treatment that specifies a resource a resource must 
        be defined.
        """
        entry = create_entry(
            datetime.timedelta(days=0),
            datetime.time(hour=12),
            datetime.timedelta(hours=0),
            'resource_required_test',
        )
        # make sure an exception is NOT raised when there is no treatment
        try:
            entry.clean()
            self.assertFalse(entry is None)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry with no treatment '\
                'raised an unexpected exception: \n{0}'.format(e)
            )

        # add a treatment that needs a resource
        entry.treatment = create_treatment(
            'requires_resource', 
            datetime.timedelta(hours=1), 
            True,
        )
        self.assertRaisesMessage(
            ValidationError, 
            'Resource requirement is not met.',
            entry.clean,
        )

        # now add a resource, get new exception due to duration
        entry.resource = create_resource(
            'resource',
            'resource',
        )
        self.assertRaisesMessage(
            ValidationError, 
            'Duration must be at least the minimum treament time.',
            entry.clean,
        )

        # change the duration to the min required, clean is now ok
        entry.duration = datetime.time(hour=1)
        try:
            entry.clean()
            self.assertFalse(entry is None)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry with\n'\
                'treatment resource and duration '\
                'raised an unexpected exception: \n{0}'.format(e)
            )


    def test_entry_equality_different_days(self):
        """
        Entries on different days are not equal.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time = datetime.time(hour=12)
        duration = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time,
            duration,
            'time calc test 1',
        )

        dateDelta2 = datetime.timedelta(days=1)
        entry2 = create_entry(
            dateDelta2, 
            time,
            duration,
            'time calc test 1',
        )

        self.assertFalse(entry1 == entry2)


    def test_entry_equality_identity(self):
        """
        Entries with identical dates, times and durations are equal.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
        )

        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
        )

        self.assertTrue(entry1 == entry2)


    def test_entry_equality_no_overlap_before(self):
        """
        Entries on the same day where the first ends before the second starts
        are not equal.
        """
        dateDelta = datetime.timedelta(days=0)

        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
        )

        time2 = datetime.time(hour=14)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
        )

        self.assertFalse(entry1 == entry2)


    def test_entry_equality_no_overlap_after(self):
        """
        Entries on the same day where the first starts after the second ends are
        not equal.
        """
        dateDelta = datetime.timedelta(days=0)

        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
        )

        time2 = datetime.time(hour=9)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
        )

        self.assertFalse(entry1 == entry2)


    def test_entry_equality_consecutive(self):
        """
        Entries on the same day where the first and second
        events are consecutive are not equal.
        """
        dateDelta = datetime.timedelta(days=0)

        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
        )

        time2 = entry1.time_end()
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
        )

        self.assertFalse(entry1 == entry2)


    def test_entry_equality_envelope(self):
        """
        Entries on the same day where one event encompasses the other are
        'equal' (i.e. they overlap in time).
        """
        dateDelta = datetime.timedelta(days=0)

        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=3)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
        )

        time2 = datetime.time(hour=13)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
        )

        self.assertTrue(entry1 == entry2)


    def test_entry_resource_clash_clean_raises_exception(self):
        """
        Make sure cleaning the data raises the correct Exception when there is a
        resource clash.
        """
        resource = create_resource('resource', 'resource')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
        )
        entry1.resource = resource
        entry1.save()

        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
        )
        entry2.resource = resource

        self.assertTrue(entry1 == entry2)
        self.assertRaisesMessage(
            ValidationError, 
            'Resource clash with another Entry. Please change resource or time.',
            entry2.clean,
        )


    def test_cancelled_entry_resource_clash_clean_no_exception(self):
        """
        Make sure cleaning the data raises no Exception when the entry is
        cancelled even with a resource clash.
        """
        resource = create_resource('resource', 'resource')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
        )
        entry1.resource = resource
        entry1.save()

        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
        )
        entry2.resource = resource
        entry2.cancelled = True

        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning a cancelled entry with \n'\
                'a time clash raised an unexpected exception: \n{0}'.format(e)
            )


    def test_entry_no_resource_clash_no_exception(self):
        """
        Make sure cleaning the data raises no Exception when resources don't
        clash with pre-existing entry data.
        """
        resource = create_resource('resource', 'resource')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
        )
        entry1.resource = resource
        entry1.save()

        resource2 = create_resource('resource_2', 'resource_2')

        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
        )
        entry2.resource = resource2

        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry with \n'\
                'no time clash raised an unexpected exception: \n{0}'.format(e)
            )


    def test_entry_resource_clash_can_save_existing(self):
        """
        Make sure cleaning the data raises no Exception we are just posting back.
        """
        resource = create_resource('resource', 'resource')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
        )
        entry1.resource = resource
        entry1.save()

        entry2 = Entry.objects.filter(
            date=entry1.date, 
            time=entry1.time,
        ).first()
        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry that already exists \n'\
                'raised an unexpected exception: \n{0}'.format(e)
            )


    def test_entry_resource_clash_no_resource_means_no_clash(self):
        """
        Entries using no resources do not generate any conflicts even when they
        overlap in time.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time = datetime.time(hour=12)
        duration = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time,
            duration,
            'resource_conflict_test_entry_1',
        )
        entry1.save()

        dateDelta2 = datetime.timedelta(days=0)
        entry2 = create_entry(
            dateDelta2, 
            time,
            duration,
            'resource_conflict_test_entry_2',
        )

        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry with no resources \n'\
                'raised an unexpected exception: \n{0}'.format(e)
            )


    def test_entry_customer_double_booked(self):
        """
        Make sure customer cannot double-book (irrespective of resource).
        """
        customer = create_customer('test')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'double-book test 1',
        )
        entry1.customer = customer
        entry1.save()

        entry2 = create_entry(
            dateDelta1,
            time1,
            duration1,
            'double-book test 2',
        )
        entry2.customer = customer

        self.assertTrue(entry1 == entry2) # this passes the other tests
        self.assertRaisesMessage(
            ValidationError, 
            'Double booking is not allowed. Please choose another time.',
            entry2.clean,
        )


    def test_cancelled_entry_customer_double_booked(self):
        """
        Make sure customer can double-book when one of the bookings is cancelled.
        """
        customer = create_customer('test')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'double-book test 1',
        )
        entry1.customer = customer
        entry1.cancelled = True
        entry1.save()

        entry2 = create_entry(
            dateDelta1,
            time1,
            duration1,
            'double-book test 2',
        )
        entry2.customer = customer

        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning a cancelled entry with double booking \n'\
                'raised an unexpected exception: \n{0}'.format(e)
            )


    @freeze_time('2015-10-12 12:00:00')
    def test_no_show_entry_customer_double_booked(self):
        """
        Make sure can double-book customer when one of the bookings is no-show.
        """
        customer = create_customer('test')

        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'double-book test 1',
        )
        entry1.customer = customer
        entry1.no_show = True
        entry1.save()

        entry2 = create_entry(
            dateDelta1,
            time1,
            duration1,
            'double-book test 2',
        )
        entry2.customer = customer

        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertTrue(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning a no_show entry with double booking \n'\
                'raised an unexpected exception: \n{0}'.format(e)
            )


    @freeze_time('2015-10-12 12:00:00')
    def test_entry_customer_out_of_hours(self):
        """
        Make sure customers cannot book outside trading hours.
        
        This test is patched to avoid complications with changing times.
        """

        customer = create_customer('test')

        dateDelta = datetime.timedelta(days=14)
        date = datetime.datetime.today().date()
        openingTime = settings.DIARY_OPENING_TIMES[date.weekday()]
        time1 = change_time(date, openingTime, datetime.timedelta(hours=1))
        duration = datetime.timedelta(hours=1)
        entry = create_entry(
            dateDelta,
            time1,
            duration,
            'trading hours test 1',
        )
        entry.editor = customer

        # make sure an exception is NOT raised
        try:
            entry.clean()
            self.assertTrue(entry == entry)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry with no conflicts \n'\
                'raised an unexpected exception: \n{0}'.format(e)
            )

        # now try again out of hours
        time2 = change_time(date, openingTime, datetime.timedelta(hours=-1))
        entry.time = time2
        self.assertRaisesMessage(
            ValidationError, 
            'Sorry, the store is closed then. Try changing the time.',
            entry.clean,
        )


    @freeze_time('2015-10-12 12:00:00')
    def test_entry_staff_out_of_hours(self):
        """
        Make sure staff are able to book any time.
        
        This test is patched to avoid complications with changing times.
        """

        dateDelta = datetime.timedelta(days=14)
        date = datetime.datetime.today().date()
        openingTime = settings.DIARY_OPENING_TIMES[date.weekday()]
        time1 = change_time(date, openingTime, datetime.timedelta(hours=-1))
        duration = datetime.timedelta(hours=1)
        entry = create_entry(
            dateDelta,
            time1,
            duration,
            'trading hours test 2',
        )

        # make sure an exception is NOT raised
        try:
            entry.clean()
            self.assertTrue(entry == entry)
        except Exception as e:
            traceback.print_exc()
            self.fail(
                'Cleaning an entry with no conflicts \n'\
                'raised an unexpected exception: \n{0}'.format(e)
            )


    @freeze_time('2015-10-12 12:00:00')
    def test_entry_customer_in_past(self):
        """
        Make sure customers cannot book in the past.
        
        This test is patched to provide a constant value of 'now'
        """

        customer = create_customer('test')
        dateDelta = datetime.timedelta(days=0)
        date = timezone.localtime(timezone.now()).date()
        now = timezone.localtime(timezone.now()).time()
        time = change_time(date, now, datetime.timedelta(hours=-1))
        duration = datetime.timedelta(hours=1)
        entry = create_entry(
            dateDelta,
            time,
            duration,
            'past test 1',
        )
        entry.editor = customer

        self.assertRaisesMessage(
            ValidationError, 
            'Please book a date/time in the future.',
            entry.clean,
        )


    @freeze_time('2015-10-12 12:00:00')
    def test_entry_customer_advance_limit(self):
        """
        Make sure customers cannot book before the advance limit. (Time in
        future but before the advance booking limit).
        
        This test is patched to provide a constant value of 'now'
        """

        # set up the min_booking time
        min_booking_orig = settings.DIARY_MIN_BOOKING
        setattr(main_settings, 'DIARY_MIN_BOOKING', 1)
        imp.reload(settings)

        customer = create_customer('test')
        dateDelta = datetime.timedelta(days=0)
        date = timezone.localtime(timezone.now()).date()
        now = timezone.localtime(timezone.now()).time()
        time = change_time(date, now, datetime.timedelta(hours=1))
        duration = datetime.timedelta(hours=1)
        entry = create_entry(
            dateDelta,
            time,
            duration,
            'advance test',
        )
        entry.editor = customer

        self.assertRaisesMessage(
            ValidationError, 
            'Need to book ahead.',
            entry.clean,
        )

        # reset the settings
        setattr(main_settings, 'DIARY_MIN_BOOKING', min_booking_orig)
        imp.reload(settings)



class ViewTests(TestCase):
    """
    Tests of various aspects of the diary views and behavior.
    """


    def setup(self):
        """
        Set up a client for getting/posting the views.
        """
        User.objects.create_user('test', 'test@example.com', 'test')
        self.client.login(username='test', password='test')


    def test_login_required_for_diary(self):
        """
        Navigating to the diary automatically redirects to login page if 
        not logged in.
        """
        response = self.client.get(reverse('diary:year_now'), follow=True)
        self.assertRedirects(
            response, 
            '/accounts/login/?next=/diary/year/',
        )


    def test_cal_first_day_of_week_default(self):
        """
        Make sure the custom setting for day of week works.
        """
        self.setup()

        # test the default
        response = self.client.get(reverse('diary:month_now'))
        self.assertEqual(response.context['day_names'][0], 'Monday')


    def test_cal_first_day_of_week_sunday(self):
        """
        Make sure the custom setting for day of week works.
        """
        self.setup()
        first_day_of_week_orig = settings.DIARY_FIRST_DAY_OF_WEEK
        setattr(main_settings, 'DIARY_FIRST_DAY_OF_WEEK', 6)

        # test for sunday
        imp.reload(settings)
        imp.reload(views)
        response = self.client.get(reverse('diary:month_now'))
        self.assertEqual(response.context['day_names'][0], 'Sunday')

        # tidy up the mess (make sure default is restored)
        setattr(main_settings, 'DIARY_FIRST_DAY_OF_WEEK', first_day_of_week_orig)
        imp.reload(settings)
        imp.reload(views)
        response = self.client.get(reverse('diary:month_now'))
        self.assertEqual(response.context['day_names'][0], 'Monday')

