from django.conf.urls import url
from . import views


urlpatterns = [
    # catch-all home page only used for testing (we hope?)
    url(r'', views.home, name='home'),
]
