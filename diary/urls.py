from django.conf.urls import url
from . import views


urlpatterns = [

    # year and month views
    url(r'^year/(?P<year>\d{4})/$', views.year, name='year',),
    url(r'^year/$', views.year, name='year_now'),   # default is this year
    url(r'^month/(?P<year>\d{4})/(?P<month>\d+)/(?P<change>prev|next)/$',
        views.month,
        name='month_nav',
    ),
    url(r'^month/(?P<year>\d{4})/(?P<month>\d+)/$', 
        views.month,
        name='month',
    ),
    url(r'^month/$', views.month, name='month_now'),# default is this month


    # slug format multi-day views. this is the default landing area
    url(r'^multi_day/(?P<slug>\d{4}-\d\d-\d\d)/(?P<change>prev|next)/$', 
        views.multi_day,
        name='multi_day_nav',
    ),
    url(r'^multi_day/(?P<slug>\d{4}-\d\d-\d\d)/$', 
        views.multi_day,
        name='multi_day',
    ),
    url(r'^multi_day/$', 
        views.multi_day, 
        name='multi_day_now',
    ),                                              # default day is today
    url(r'^multi_day/$', 
        views.multi_day, 
        name='home'
    ),                                              # 'home' page


    # slug format day views
    url(
        r'^day/(?P<slug>\d{4}-\d\d-\d\d)/(?P<change>prev|next)/$',
        views.day,
        name='day_nav',
    ),
    url(r'^day/(?P<slug>\d{4}-\d\d-\d\d)/$', views.day, name='day'),
    url(r'^day/$', views.day, name='day_now'),      # default day is today


    # slug format entry views
    url(r'^entry/(?P<slug>\d{4}-\d\d-\d\d_\d\d-\d\d)/$', 
        views.entry,
        name='entry_new'
    ),
    url(r'^entry/(?P<slug>\d{4}-\d\d-\d\d_\d\d-\d\d)/(?P<customer_pk>\d+)/$', 
        views.entry,
        name='entry_new_customer'
    ),
    url(r'^entry/(?P<pk>\d+)/(?P<customer_pk>\d+)$', 
        views.entry, 
        name='entry_customer',
    ),
    url(r'^entry/(?P<pk>\d+)/$', views.entry, name='entry',),
    url(r'^entry/$', 
        views.entry, 
        name='entry_empty',
    ),                                              # default is create new
    url(r'^entry_admin/(?P<pk>\d+)/(?P<action>cancel|no_show|delete)/$',
        views.entry_admin, 
        name='entry_admin',
    ),


    # for drag-and-drop with ajax
    url(r'^entry_update/$', views.entry_update, name='entry_dnd',),


    # ajax dynamic modals
    url(r'^entry_modal/(?P<pk>\d+)/$', views.entry_modal, name='entry_modal',),


    # customer administration - overrides admin pages to control redirection
    url(r'^customer_add/(?P<entry_pk>\d+)/$', 
        views.customer_add, 
        name='customer_add_entry_pk',               # existing entry pk
    ),
    url(r'^customer_add/(?P<entry_slug>\d{4}-\d\d-\d\d_\d\d-\d\d)/$', 
        views.customer_add, 
        name='customer_add_entry_slug',             # new entry slug
    ),
    url(r'^customer_add/$', 
        views.customer_add, 
        name='customer_add',                        # default has no entry
    ),

    # edit customer
    url(r'^customer_change/(?P<pk>\d+)/$', 
        views.customer_change, 
        name='customer_edit',                       # edit customer
    ),
    url(r'^customer_change/$', 
        views.customer_change, 
        name='customer_change',                     # default is current user
    ),

    # customer history
    url(r'^history/(?P<pk>\d+)/$', 
        views.history, 
        name='history',                             # review treatment history
    ),
    url(r'^history/$', 
        views.history, 
        name='history_default',                     # default is current user
    ),

]
