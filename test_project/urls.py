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
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$',
        auth_views.logout,
        {'next_page': '/'},
        name='logout'),
    url(r'^accounts/password/reset/$',
        auth_views.password_reset,
        {'post_reset_redirect' : '/accounts/password/reset/done/'},
        name='password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect' : '/accounts/password/done/'},
        name='password_reset_confirm'),
    url(r'^accounts/password/done/$', auth_views.password_reset_complete),
    url(r'^diary/', include('diary.urls', namespace='diary')),
    url(r'', include('home.urls')),
]
