from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Customer


class CustomerAuthBackend(ModelBackend):
    """
    Home-spun backend in response to django-model-utils functionality not
    working for Django >~ 2
    """
    def get_user(self, user_id):
        try:
            return Customer.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, username=None, password=None):
        try:
            user = Customer.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
