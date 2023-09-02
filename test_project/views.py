from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.contrib.auth import logout as logout_user
from test_project.settings import LOGOUT_REDIRECT_URL


def logout(request):
    logout_user(request)
    # Redirect to a success page.
    response = redirect(LOGOUT_REDIRECT_URL)
    return response
