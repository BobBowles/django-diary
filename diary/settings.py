from django.conf import settings
import datetime

"""
Custom settings and their defaults for the diary app are defined here.
"""

def get(key, default):
    """
    Obtain any user-supplied values set in the main settings.py.
    """
    value = getattr(settings, key, default)
    #print('Setting {0} set to: {1}'.format(key, value))
    return value


# first day of week defaults to Monday = 0
DIARY_FIRST_DAY_OF_WEEK = get('DIARY_FIRST_DAY_OF_WEEK', 0)

# number of days on multi-day display defaults to 3
DIARY_MULTI_DAY_NUMBER = get('DIARY_MULTI_DAY_NUMBER', 3)

# whether to use meridian format defaults to False
DIARY_SHOW_MERIDIAN = get('DIARY_SHOW_MERIDIAN', False)

# earliest time to display on day and multi_day views defaults to 08:00
DEFAULT_MIN_TIME = datetime.time(hour=8)
DIARY_MIN_TIME = get('DIARY_MIN_TIME', DEFAULT_MIN_TIME)

# latest time to display on day and multi_day views defaults to 18:00
DEFAULT_MAX_TIME = datetime.time(hour=18)
DIARY_MAX_TIME = get('DIARY_MAX_TIME', DEFAULT_MAX_TIME)

# time slot increment for day and multi_day views defaults to 00:30
DEFAULT_TIME_INC = datetime.timedelta(minutes=30)
DIARY_TIME_INC = get('DIARY_TIME_INC', DEFAULT_TIME_INC)

# opening times keyed by weekday number
DEFAULT_OPENING_TIME = datetime.time(hour=9)
DEFAULT_OPENING_TIMES = {n: DEFAULT_OPENING_TIME for n in range(0, 7)}
DIARY_OPENING_TIMES = get('DIARY_OPENING_TIMES', DEFAULT_OPENING_TIMES)

# closing times keyed by weekday number
DEFAULT_CLOSING_TIME = datetime.time(hour=17)
DEFAULT_CLOSING_TIMES = {n: DEFAULT_CLOSING_TIME for n in range(0, 7)}
DIARY_CLOSING_TIMES = get('DIARY_CLOSING_TIMES', DEFAULT_CLOSING_TIMES)

# minimum advance booking time for customers in days
DIARY_MIN_BOOKING = get('DIARY_MIN_BOOKING', 0)

# site name for use by email_reminder
DIARY_SITE_NAME = get('DIARY_SITE_NAME', 'Django-Diary')

# contact phone number for use by email_reminder
DIARY_CONTACT_PHONE = get('DIARY_CONTACT_PHONE', '')

