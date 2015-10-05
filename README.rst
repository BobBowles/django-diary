Django Diary
============


Description
-----------

Django-Diary is a project to create an easy-to-use desk diary and scheduling tool for use in a fast-paced retail environment. The aim is to be able to schedule and manage client bookings with available resources as quickly and easily as possible with no fuss.


The Models
----------

The diary model has deliberately been made very simple. It is built on the foundation of practical experience manning the front desk of a health clinic. It needs to be easy and fast to use.

The core concept is a diary ``Entry``, which records the date and time of an appointment with a ``Customer``, which may use a time-allocated ``Resource``. The ``Duration`` of each booking is determined by the type of ``Treatment`` to be administered.

There are no repeating entries; while it is expected that customers will make repeat bookings, it is assumed the repeat bookings will *not* follow any simple rule. So, to avoid complexity that will not actually be useful, all diary entries are considered as unique and unrelated occurrences. This is in stark contrast to popular (and very fine) calendar/scheduling apps like ``django-schedule`` and ``django-calendarium``.

Entries are allowed to overlap in time, provided there are no resource conflicts. If a resource is assigned to an entry, no other entry can use the same resource at the same time.

Customers are ``Users`` of the system, but they have additional attributes. In keeping with the health clinic paradigm, they have demographic and health-related information associated with them, contact details, and of course their treatment history, which can be derived from their historical record of appointments.

In the interests of confidentiality, customers may only see and alter their own details and appointments. Staff members are able to see and alter the details of all entries.


Installation
------------

A complete sample project is available on `GitHub <https://github.com/BobBowles/django-diary>`_ for forking or clone/download, but for use as a standalone app install from `PyPi <https://pypi.python.org/pypi/django-diary/>`_ using ``pip``.

1.  Install ``django-diary`` and its dependencies using ``pip``::

        pip install django-diary


#.  Add ``diary`` and ``datetimewidget`` to your ``INSTALLED_APPS`` in ``settings.py``:

    ::

        ...
            'diary',
            'datetimewidget',
        ...

#.  Run the migrations:

    ::

        ./manage.py migrate


#.  Also in ``settings.py`` configure meridian time displays [TODO: if you are using them - need configuration option]:

    ::

        # the django default does not allow time with meridian
        TIME_INPUT_FORMATS = (
            '%H:%M:%S',
            '%H:%M',
            '%I %p',
            '%I:%M %p',
            '%I:%M%p',
            '%H:%M:%S.%f',
        )


#.  Add the following to ``settings.py`` to enable the use of the ``Customer`` subclass of ``User``:

    ::

        # User customisation
        # NOTE: use of InheritanceQuerySet in the backend dispenses with the need for 
        # any other setting. (django-model-utils)
        # http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/
        AUTHENTICATION_BACKENDS = (
            'diary.backends.CustomUserModelBackend',
        )

#.  Override ``templates/diary/main_base.html`` to customise layout and styling for your site. ``main_base.html`` (and/or its parents) need to provide the following five blocks:

    ==================== =======================================================
    Block                Description
    ==================== =======================================================
    **head_extra**       for adding elements to the document head
    **diary_nav**        for navigating between diary views. The nav-bar itself
                         can
                         be completely re-written to your tastes, subject only
                         to providing link placeholders described in the example 
                         implementation provided.
    **diary_content**    attachment point for the diary content.
    **diary_title**      attachment point for the page title.
    **diary_sidebar**    *(Optional)* attachment point for reminders / ticker
                         information if required.
    ==================== =======================================================

#.  Optionally configure the customisable parameters in ``settings.py``:

    ::

        DIARY_FIRST_DAY_OF_WEEK     # default=0 (Monday)
        DIARY_MULTI_DAY_NUMBER      # default=3 (show 3 days on multi-day page)
        DIARY_XXXXX                 # TODO: some documentation would be nice :)

#.  Set up the ``diary`` app's urls, and (if you want to use the customer administration) the administration urls. In your root ``urls.py`` you need the following ``urlpatterns``:

    ::

        url(r'^admin/', include(admin.site.urls)),
        url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
        url(r'^accounts/logout/$', 
            'django.contrib.auth.views.logout', 
            {'next_page': '/'}),
        url(r'^accounts/password/reset/$', 
            'django.contrib.auth.views.password_reset', 
            {'post_reset_redirect' : '/accounts/password/reset/done/'},
            name="password_reset"),
        url(r'^accounts/password/reset/done/$',
            'django.contrib.auth.views.password_reset_done'),
        url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
            'django.contrib.auth.views.password_reset_confirm', 
            {'post_reset_redirect' : '/accounts/password/done/'},
            name='password_reset_confirm'),
        url(r'^accounts/password/done/$', 
            'django.contrib.auth.views.password_reset_complete'),
        url(r'^diary/', include('diary.urls', namespace='diary')),

#.  For the password administration you need to set up an email service. For testing purposes, you can use Python's built-in dummy server. This just prints out the result of email requests on the console. From the command line:

    ::

        python -m smtpd -n -c DebuggingServer localhost:1025


#.  In your ``settings.py`` add your email server's details. For testing, the following snippet is sufficient to link to the test email server described above:

    ::

        # test email server setup
        if DEBUG:
            EMAIL_HOST = 'localhost'
            EMAIL_PORT = 1025
            EMAIL_HOST_USER = ''
            EMAIL_HOST_PASSWORD = ''
            EMAIL_USE_TLS = False
            DEFAULT_FROM_EMAIL = 'testing@example.com'



Dependencies
------------

At the fundamental level the dependencies of this app are recorded in the ``requirements.txt`` file.

The styling, layout, widgets, and javascript all utilize Twitter Bootstrap and jQuery. Hopefully the dependencies are self-contained, but obviously it is more harmonious if your project as a whole is designed around Bootstrap.

I have made no effort to write this for Python 2.7, targeting Python 3 from the outset, and specifically Python 3.4. I intend to look at that at a future date.

The Python/Django package dependencies are as follows::

    Django==1.8.3
    django-datetime-widget==0.9.3
    django-model-utils==2.3.1
    pytz==2015.4
    six==1.9.0

Although they are listed here as strict requirements, they are probably more accurately *minimum* requirements. However, while I am continuing to develop the code I am opting for a simple life...

**Django**
    is self-explanatory. At time of writing I am still actively developing, so I am focusing only on Django 1.8. At some point I intend to improve coverage, but the demand at present is to get something-that-works.

**django-datetime-widget**
   is a project to provide some nice Bootstrap date and time widgets for Django. It needs to be added as an app in the settings file. To use meridian time, the time formats also need to be added to the settings, as the Django defaults ignore meridian. The code looks something like this::

    TIME_INPUT_FORMATS = (
        '%H:%M:%S',
        '%H:%M',
        '%I %p',
        '%I:%M %p',
        '%I:%M%p',
        '%H:%M:%S.%f',
    )

**django-model-utils**
    is a project that provides a number of useful tools for manipulating models. It is primarily used here for facilitating subclassing of User.

**pytz**
    is needed for date and time manipulation.

**six**
    was dragged in at some point by one of the above (I think).


Reusability
-----------

At this early stage reusability is an aspiration rather than a reality. To achieve this the following considerations have been/need to be made:

*  Overriding of templates and styles. A main_base.html template has been constructed that forms the basis of a working example of the app, and at the same time provides a starting point for overriding. Attention also needs to be given to navigation hooks.
*  Configuration. While wanting the diary app to be configurable for different scenarios, it is also important to keep focused on core function and _not_ provide too many hooks. A ``settings.py`` file exists in the diary which provides default values for a few parameters that can be overridden in the project's settings file. For easy discrimination, all configurable parameters have names of the form ``DIARY_XXXXX``. The parameter names will be chosen to be reasonably self-explanatory, and (eventually) will be documented somewhere.
*  Dependencies. Kept to a minimum. They will be documented (promise!).
*  Debate about using a subclass of ``User`` for ``Customer``. This may adversely affect reusability, but may have been mitigated by ``django-model-utils`` for subclass manipulation.


Design Considerations
---------------------

Ease of use is paramount, because it is intended the application will be used by people unversed in software. Use of the app needs to be simple and intuitive.

Web deployment was decided upon at an early stage, because this enables use of the app from more than one location. The web server may be local or on the internet. One use case I had in mind was being able to check/modify the diary when at home, as well as at work.

The decision for web deployment, coupled with a preference for Python as the main language, led naturally to using Django as the framework. This also gives flexibility of choice for the database engine, as the Django settings will automatically take care of that, provided appropriate Python drivers are installed.

Django-Calendarium was initially chosen as the calendar/diary engine after some consideration of the options available. However, although hooks are available, they were not located in what I regarded as convenient places to do what I wanted to do. I tentatively played with some other calendar/scheduling apps, and reluncantly decided I needed to brew my own to get what I wanted.

I found a tutorial by LightBird. Although the code was terrible and outdated, it gave me a model workflow to follow as I both developed a calendar app and learned Django, JavaScript, CSS, HTML5, and other necessary technologies.

I eventually decided to subclass ``User`` to make a custom user class called ``Customer``. I did that to enable a tight relationship between customers as users and diary entries in the simplest possible way. Other options seemed to involve jumping through too many database join hoops. This may work against reusability of this app, but I think the tweaks I have put into the admin backend may mitigate this. In principle the admin backend in this app should be able to accommodate other custom users, but I may not have given enough attention to that possibility in my own code. It will be interesting to get feedback about that from devs, so keep me posted! 


History
-------

This started out as a series of experimental projects built on top of Django tutorials, and explorations of existing Django calendar apps and other Django snippets:

1. `Django Project Tutorial <https://docs.djangoproject.com/en/1.8/intro/tutorial01/>`_

2. `Django Girls <https://djangogirls.org/>`_

3. `LightBird Calendar Tutorial <http://lightbird.net/dbe/cal1.html>`_

4. `Django Scheduler <https://github.com/llazzaro/django-scheduler>`_

5. `Django Calendarium <https://github.com/bitmazk/django-calendarium>`_

