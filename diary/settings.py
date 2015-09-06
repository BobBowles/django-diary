from django.conf import settings

"""
Custom settings and their defaults for the diary app are defined here.
"""

def get(key, default):
    return getattr(settings, key, default)


DIARY_FIRST_DAY_OF_WEEK = get('DIARY_FIRST_DAY_OF_WEEK', 0)
DIARY_MULTI_DAY_NUMBER = get('DIARY_MULTI_DAY_NUMBER', 3)

