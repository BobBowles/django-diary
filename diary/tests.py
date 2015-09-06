from django.test import TestCase
from django.test.utils import override_settings
from .models import Entry
from django.utils import timezone
import datetime
from django.forms import ValidationError
import traceback
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
#from . import settings
from django.conf import settings as main_settings
from . import settings
from . import views
import importlib as imp         # since Python 3.4

# Create your tests here.

from .models import Customer
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


#    def test_anonymous_customer_exists(self):
#        """
#        Check that there is an anonymous customer for use by the diary app.
#        """
#        anonymousCustomer = Customer.objects.get(username='anon')
#        self.assertIsNotNone(anonymousCustomer)


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



def create_entry(dateDelta, time, duration, title, snippet, body):
    """
    Utility to create an entry for testing.
    Updated to use timefield for duration.
    """
    date = timezone.datetime.today() + dateDelta
    duration_as_time = (
        datetime.datetime.combine(date, TIME_ZERO) + duration
    ).time()
    return Entry(
        title=title,
        snippet=snippet,
        body=body,
        date=date,
        time=time,
        duration=duration_as_time, # duration in the database is really a time
    )



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
            'time calc test 1',
            'time calc test 1',
        )
        result = datetime.time(hour=13)
        self.assertEqual(entry.time_end(), result)


    def test_entry_time_relation_eq_different_days(self):
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
            'time calc test 1',
            'time calc test 1',
        )
        dateDelta2 = datetime.timedelta(days=1)
        entry2 = create_entry(
            dateDelta2, 
            time,
            duration,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_identity(self):
        """
        Entries with identical dates, times, and durations are equal.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
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
            'time calc test 1',
            'time calc test 1',
        )
        self.assertTrue(entry1 == entry2)


    def test_entry_time_relation_eq_before(self):
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
            'time calc test 1',
            'time calc test 1',
        )
        time2 = datetime.time(hour=14)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_after(self):
        """
        Entries on the same day where the first starts after the second ends
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
            'time calc test 1',
            'time calc test 1',
        )
        time2 = datetime.time(hour=9)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_consecutive(self):
        """
        Entries on the same day where the first and second events are 
        consecutive are not equal.
        """
        dateDelta = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        time2 = entry1.time_end()
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertFalse(entry1 == entry2)


    def test_entry_time_relation_eq_envelope(self):
        """
        Entries on the same day where one event encompasses the other are 
        'equal'.
        """
        dateDelta = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=3)
        entry1 = create_entry(
            dateDelta, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        time2 = datetime.time(hour=13)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertTrue(entry1 == entry2)


    def test_entry_time_relation_clean_clash(self):
        """
        Make sure cleaning the data raises the correct Exception when times
        clash with pre-existing entry data.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        entry1.save()
        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=12)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        self.assertTrue(entry1 == entry2)
        self.assertRaisesMessage(
            ValidationError, 
            'Time clash not allowed. Please change the date/time/duration.',
            entry2.clean,
        )


    def test_entry_time_relation_clean_no_clash(self):
        """
        Make sure cleaning the data raises no Exception when times do not
        clash with pre-existing entry data.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        entry1.save()
        dateDelta2 = datetime.timedelta(days=0)
        time2 = datetime.time(hour=14)
        duration2 = datetime.timedelta(hours=1)
        entry2 = create_entry(
            dateDelta2, 
            time2,
            duration2,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
        # make sure an exception is NOT raised
        try:
            entry2.clean()
            self.assertFalse(entry1 == entry2)
        except Exception as e:
            traceback.print_exc()
            self.fail(
    'Cleaning an entry with no time clash raised an unexpected exception: {0}'
    .format(e)
            )


    def test_entry_time_relation_clean_save_existing(self):
        """
        Make sure cleaning the data raises no Exception we are just posting back.
        """
        dateDelta1 = datetime.timedelta(days=0)
        time1 = datetime.time(hour=12)
        duration1 = datetime.timedelta(hours=1)
        entry1 = create_entry(
            dateDelta1, 
            time1,
            duration1,
            'time calc test 1',
            'time calc test 1',
            'time calc test 1',
        )
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
    'Cleaning an entry that already exists raised an unexpected exception: {0}'
    .format(e)
            )


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
        response = self.client.get(reverse('diary.views.year'))
        self.assertRedirects(
            response, 
            '/accounts/login/?next=/diary/',
        )


    def test_cal_first_day_of_week_default(self):
        """
        Make sure the custom setting for day of week works.
        """
        self.setup()

        # test the default
        response = self.client.get(reverse('diary.views.month'))
        self.assertEqual(response.context['day_names'][0], 'Monday')


    def test_cal_first_day_of_week_sunday(self):
        """
        Make sure the custom setting for day of week works.
        """
        self.setup()
        setattr(main_settings, 'DIARY_FIRST_DAY_OF_WEEK', 6)

        # test for sunday
        imp.reload(settings)
        imp.reload(views)
        response = self.client.get(reverse('diary.views.month'))
        self.assertEqual(response.context['day_names'][0], 'Sunday')

        # tidy up the mess (make sure default is restored)
        setattr(main_settings, 'DIARY_FIRST_DAY_OF_WEEK', 0)
        imp.reload(settings)
        imp.reload(views)
        response = self.client.get(reverse('diary.views.month'))
        self.assertEqual(response.context['day_names'][0], 'Monday')

