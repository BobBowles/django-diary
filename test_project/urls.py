"""test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include
from django.urls import re_path as url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$',      # Stop using class view to force logout by post (Django 5)
        views.logout,
        name='logout',
    ),
    url(r'^accounts/password_reset/$',
        auth_views.PasswordResetView.as_view(),
        name = 'password_reset',
    ),
    url(r'^accounts/password_reset/password_reset_done/$',
        auth_views.PasswordResetDoneView.as_view(),
        name = 'password_reset_done',
    ),
    url(r'^accounts/password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView.as_view(),
        name = 'password_reset_confirm',
    ),
    url(r'^accounts/password_reset_complete/$',
        auth_views.PasswordResetCompleteView.as_view(),
        name = 'password_reset_complete',
    ),
    url(r'^diary/', include('diary.urls', namespace='diary')),
    url(r'', include('home.urls')),
]
