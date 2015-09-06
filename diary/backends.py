from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from model_utils.managers import InheritanceQuerySet
from django.apps import apps
from django.conf import settings


class CustomUserModelBackend(ModelBackend):
    """
    Adapted from 
    http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/
    This version allows multiple inheritance models from User, without the cruft 
    of extra settings, by virtue of django-model-utils. This _should_ allow
    different classes of User to login and use the system, remaining 
    identifiable as different classes.
    """
    def get_user(self, user_id):
        try:
            return InheritanceQuerySet(User).select_subclasses().get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, username=None, password=None):
        try:
            user = InheritanceQuerySet(User).select_subclasses().get(
                username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None

