============
Django Diary
============


Description
-----------

Django-Diary is a project to create an easy-to-use desk diary and scheduling tool for use in a fast-paced retail environment. The aim is to be able to schedule and manage client bookings with available resources as quickly and easily as possible with no fuss.

While the data model is very simple, some effort has been put into making the UI slick and intuitive, with ``ajax`` enabling drag-and-drop and updates of modal displays on the diary grid, and ``Bootstrap``-compatible widgets used on the forms.

An additional management command is included to permit routine administration of email reminders (see `Administration`_).


The Models
----------

The diary model has deliberately been made very simple. It is built on the foundation of practical experience manning the front desk of a health clinic. It needs to be easy and fast to use.

The core concept is a diary ``Entry``, which records the date and time of an appointment with a ``Customer``, which may use a time-allocated ``Resource``. The ``Duration`` of each booking is determined by the type of ``Treatment`` to be administered.

There are no repeating entries; while it is expected that customers will make repeat bookings, it is assumed the repeat bookings will *not* follow any simple rule. So, to avoid complexity that will not actually be useful, all diary entries are considered as unique and unrelated occurrences. This is in stark contrast to popular (and very fine) calendar/scheduling apps like ``django-schedule`` and ``django-calendarium``.

Entries are allowed to overlap in time, provided there are no resource conflicts. If a resource is assigned to an entry, no other entry can use the same resource at the same time. Entries that have been cancelled do not count when evaluating resource conflicts.

There are two categories of ``User``. The standard admin ``Users`` are retained for administrative functions, and typically have at least ``is_staff`` privilege.

Customers are also ``Users`` of the system (they are in fact a subclass of ``User``). While they have no administrative privileges, they have additional attributes. In keeping with the health clinic paradigm, they have demographic and health-related information associated with them, contact details, and of course their treatment history, which can be derived from their historical record of appointments. Customers have the choice to opt out of email appointment reminders and appointment change notifications.

In the interests of confidentiality, ``Customers`` may only see and alter their own details and appointments. Staff ``Users`` are able to see and alter the details of all entries.


Installation
------------

A complete sample project is available on `GitHub <https://github.com/BobBowles/django-diary>`_ for forking or clone/download, but for use as a standalone app install from `PyPi <https://pypi.python.org/pypi/django-diary/>`_ using ``pip``.

1.  Install ``django-diary`` and its dependencies using ``pip``::

        pip install django-diary

    For versions >= 2 this may need to be a two-stage process due to references to package forks not in Pypi (TBA)::

        pip install django-diary --no-deps  # installs the app by itself
        pip install django-diary            # installs the dependencies


#.  Add ``diary`` and ``datetimewidget`` underneath your main project app in
        ``settings.py``

    ::

        INSTALLED_APPS = [
        ...
            'diary',
            'datetimewidget',
        ...
        ]


#.  For better forms layouts add ``crispy_forms`` and its template pack for ``Bootstrap 3`` to your ``INSTALLED_APPS`` in ``settings.py``

    ::

        INSTALLED_APPS = [
        ...
            'crispy_forms',
            'crispy-bootstrap3'
        ...
        ]
        CRISPY_TEMPLATE_PACK = 'bootstrap3'


#.  Add the following to your ``settings.py`` for Django >= 3.2

    ::

        ...
            DEFAULT_AUTO_FIELD='django.db.models.AutoField'
        ...


#.  Run the migrations:

    ::

        ./manage.py migrate


#.  Change the authentication backend to enable the use of the ``Customer`` subclass of ``User``. Add the following to ``settings.py`` (NB This is different for Django<2, check the documentation in the v1 branch of this project.):

    ::

        # User customisation
        AUTHENTICATION_BACKENDS = (
            'diary.backends.CustomerAuthBackend',
            'django.contrib.auth.backends.ModelBackend',
        )

#.  Set up the ``diary`` app's urls, and (if you want to use the customer administration) the administration urls. In your root ``urls.py`` you need the following ``urlpatterns``:

    ::

        from django.contrib.auth import views as auth_views
        ...
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

#.  For password administration, the email reminder service, and admin entry tracking you need to set up an email service. It is sufficient to use Python's built-in dummy server for development and testing. This just prints out the result of email requests onto the console. From the command line:

    ::

        python -m smtpd -n -c DebuggingServer localhost:1025

    (or just use the bash script checked into the `GitHub project <https://github.com/BobBowles/django-diary>`_). Alternatively, and even more easily, ``Django`` provides a console email backend that can be implemented in place of the default smtp backend in ``settings.py`` as follows:

    ::

        # test email server console backend
        if DEBUG:
            EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    In your ``settings.py`` add your email server's details. The following snippet links to the dummy email server described above:

    ::

        # test email server setup
        if DEBUG:
            EMAIL_HOST = 'localhost'
            EMAIL_PORT = 1025
            EMAIL_HOST_USER = ''
            EMAIL_HOST_PASSWORD = ''
            EMAIL_USE_TLS = False
            DEFAULT_FROM_EMAIL = 'testing@example.com'
            ADMINS = [
                ('Admin 1', 'admin1@example.com'),
                ('Admin 2', 'admin2@example.com'),
            ]

    Configuring the ``ADMINS`` list enables monitoring of diary entries via email. This is a useful feature to keep track of ``customer``-initiated changes in the diary. If not wanted, leave the ``ADMINS`` list empty or null.


Configuration
-------------

After installation you should have 'something-that-works' but it will look ugly round the edges and the behaviour will need fine-tuning to your business requirements.


1.  Override ``templates/diary/main_base.html`` to customise layout and styling for your site. ``main_base.html`` (and/or its parents) need to provide the following five blocks:

    =================== ========================================================
    Block               Description
    =================== ========================================================
    ``head_extra``      for adding elements to the document head. Add Bootstrap
                        css links here if they are not already in your template
                        header.
    ``diary_nav``       for navigating between diary views. The nav-bar itself
                        can be completely re-written to your tastes, subject
                        only to providing link placeholders described in the
                        example implementation provided.
    ``diary_content``   attachment point for the diary content.
    ``diary_title``     attachment point for the page title.
    ``diary_sidebar``   *(Optional)* attachment point for reminders / ticker
                        information if required. This block should include the
                        html snippet ``diary/reminders.html`` (which may also be
                        overridden if required).
    =================== ========================================================

#.  For staging and production supply the parameters for your email service in your ``settings.py``. The test email service described in the Installation section above provides a ready-made template for the required parameters. Make sure you connect to your provider's SMTP service port. Below is an example for a Google account:

    ::

            EMAIL_HOST = 'smtp.gmail.com'
            EMAIL_PORT = 587
            EMAIL_USE_TLS = True
            DEFAULT_FROM_EMAIL = 'webmaster@mygoogledomain.com'
            EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
            EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
            ADMINS = os.environ['ADMINS']

    (Note the use of environment variables to keep sensitive information out of your revision control system. There are other ways to do this but this is pretty cool and simple).

#.  Optionally configure the customisable diary parameters in ``settings.py``:

    =========================== =========== =========== ========================
    Parameter                   Default     Type        Description
    =========================== =========== =========== ========================
    ``DIARY_FIRST_DAY_OF_WEEK`` ``0``       int         The first day of the
                                                        week for month views and
                                                        calendar widgets
                                                        (``0='Monday'``.
                                                        For Sunday as first day
                                                        set to ``6``).
    ``DIARY_MULTI_DAY_NUMBER``  ``3``       int         The number of days to
                                                        show in the multi-day
                                                        view. ``3`` is a
                                                        minimum.
                                                        The practical maximum is
                                                        ``7``.
    ``DIARY_SHOW_MERIDIAN``     ``False``   bool        Enable display of times
                                                        in meridian format.
                                                        **NB**: If ``True`` some
                                                        additional configuration
                                                        is needed to enable
                                                        *input* of meridian
                                                        times (see below).
    ``DIARY_MIN_TIME``          ``08:00``   time        The earliest time to
                                                        display in ``day`` and
                                                        ``multi_day`` views.
    ``DIARY_MAX_TIME``          ``18:00``   time        The latest time to
                                                        display in ``day`` and
                                                        ``multi_day`` views.
    ``DIARY_TIME_INC``          ``00:30``   duration    The size of time slots
                                                        for ``day`` and
                                                        ``multi_day`` views.
    ``DIARY_OPENING_TIMES``                 dict        Dictionary of opening
                                                        times keyed on weekday
                                                        number. Default is 09:00
                                                        all week.
    ``DIARY_CLOSING_TIMES``                 dict        Dictionary of closing
                                                        times keyed on weekday
                                                        number. Default is 17:00
                                                        all week.
    ``DIARY_MIN_BOOKING``       ``0``       int         Minimum advance booking
                                                        time for customers in
                                                        days. ``0`` means there
                                                        is no minimum period.
    ``DIARY_SITE_NAME``         ``Django-   str         Name of site for use
                                Diary``                 in emails.
    ``DIARY_CONTACT_PHONE``     ``''``      str         Contact phone number for
                                                        use in emails.
    ``DIARY_XXXXX``             ``xx``      xx          **TODO**: Template
                                                        for ``DIARY_XXXXX``.
    =========================== =========== =========== ========================

#.  To permit the use of meridian time display and input in Django 4+ overrides must be provided in a formats directory. The following entry in ``settings.py`` enables the localisation to find the overrides for the Python defaults:

    ::


            # To use meridian time in Django 4+ we have to provide custom overrides for the localisation
            FORMAT_MODULE_PATH = [
                "diary.formats",
            ]


Administration
--------------

A custom command has been added to help maintain the database. ``clean_entries`` deletes all diary entries older than a given age, or earlier than a given date, to help reduce bloat. Usage::

    > python manage.py clean_entries [-a|--age n][-b|--before=<yyyy-mm-dd>]

A custom command has been added to enable easy implementation of the routine task of sending out email reminders. At the moment configuration settings for this are kept to a minimum, requiring a name for the site, given as ``DIARY_SITE_NAME``, and an optional contact phone number ``DIARY_CONTACT_PHONE``, plus the correct configuration of the email facility itself.

To make administration of the site easier the ``resource`` and ``treatment`` objects have been made editable inline since Version 4.2.2.

Most of the email configuration is covered in the `Installation`_ and `Configuration`_ sections. To make use of administration notifications, two email settings are needed in ``settings.py``, for ``ADMINS`` and ``SERVER_EMAIL``. The ``ADMINS`` receive reports on the email reminders, and the ``SERVER_EMAIL`` is the email account used for the mail-out. For example::

    # list of tuples of administrator names and emails
    ADMINS = [
        ('Boss 1', 'boss1@example.com),
        ('Boss 2', 'boss2@example.com),
    ]

    # server email address
    SERVER_EMAIL = 'webmaster@example.com'

Additionally, make sure the ``DEFAULT_FROM_EMAIL`` refers to a mailbox that can be replied to.

The code assumes reminders are required only for those ``Customers`` with emails who have an ``Entry`` in the diary for the following day.

To run the email reminders from the command line, in the root project directory type::

    ./manage.py email_reminder

The simplest way to schedule reminders for regular use is via a daily ``cron`` job on your server.


Dependencies and Versioning
---------------------------

At the fundamental level the dependencies of this app are recorded in the ``requirements.txt`` file.

The styling, layout, widgets, and javascript all utilize Twitter Bootstrap and jQuery. The Javascript dependencies are self-contained, but obviously it is more harmonious if your project as a whole is designed around Bootstrap. If the Bootstrap styling css is not already declared in your template's header you will need to add it.

I have made no effort to write this for Python 2.7, targeting Python 3 from the outset, initially Python 3.4. From V0.3.5 the target Python is 3.8, and support for Python 3.4 has now been dropped. Python 3.8 is maintained for maintenance branches v1, v2, and v3. From maintenance v4 and ongoing development at time of writing the target is Python 3.11.8.

Going forward I intend to support a maintenance-only release for each major version of ``Django``, plus new features to be added for the latest ``Django``.

The recommended Python/Django package dependencies are as follows for the different versions.

Version 1.x < 2 (Django 1 Maintenance Stream)
---------------------------------------------

::

    Django>=1.11.29, <2
    django-datetime-widget==0.9.3
    django-model-utils==3.2.0
    pytz==2020.1

Version 2.x < 3 (Django 2 Maintenance Stream)
---------------------------------------------

::

    Django>=2.2.13, <3
    django-datetime-widget2>=0.9.4
    pytz>=2020.1

Version 3.x < 3.6 (Django 3.0 Maintenance)
------------------------------------------

::

    Django>=3.0.7, <3.1
    django-datetime-widget2>=0.9.5
    pytz>=2020.1

Version 3.6 (Django 3.1 Maintenance)
------------------------------------

::

    Django==3.1.14
    django-datetime-widget2>=0.9.5
    pytz>=2023.3

Version 3.7 < 4 (Django 3.2 Maintenance)
----------------------------------------

::

    Django==3.2.20
    django-datetime-widget2>=0.9.5
    pytz>=2023.3

Version 4.2 <= 4.2.11 (Django 4 Maintenance)
--------------------------------------------

::

    Django==4.2.11, <5
    django-datetime-widget2>=0.9.5
    DateTime>=5.2
    crispy_forms>=2.1
    crispy-bootstrap3>=2022.1

Version 5+ (Django 5 Development - TBA)
---------------------------------------

::

    Django>=5.0, <6
    django-datetime-widget2>=0.9.5
    DateTime>=5.2
    crispy_forms>=2.1
    crispy-bootstrap3>=2022.1


Although they are listed here as strict requirements, they are probably more accurately *minimum* requirements. However, while I am continuing to develop the code I am opting for a simple life...

``Django``
    is self-explanatory. Up to V0.3.5 the target was Django 1.8. Following versions drop support for Django 1.8. Planned maintenance releases will cover Django 1.11.29 (v1.x), Django 2.2.13 (v2.x), Django 3.2.20 (v3.x), Django 4.2.11 (v4.x). The development stream is expected to upgrade to Django 5 when there is a stable version available.

``django-datetime-widget``
    is a project to provide some nice Bootstrap date and time widgets for ``Django``. It needs to be added as an app in the settings file. To use meridian time, the time formats also need to be added to the settings, as the ``Django`` defaults ignore meridian (see the Configuration section). The original version (0.9.3) available in Pypi is fine for ``Django<2.1``, but for ``Django>=2.1`` an updated version due to Erwin Gelissen has been published as ``django-datetime-widget2``.

``django-model-utils``
    is a project that provides a number of useful tools for manipulating models. It is primarily used here for facilitating subclassing of User. It is not needed for Django>=2.0.

``DateTime``
    is needed for date and time manipulation in Django 5 and above. This pulls in other modules such as ``pytz``.


Reusability
-----------

At this early stage reusability is an aspiration rather than a reality. To achieve this the following considerations have been/need to be made:

*  Overriding of templates and styles. A main_base.html template has been constructed that forms the basis of a working example of the app, and at the same time provides a starting point for overriding. Attention also needs to be given to navigation hooks.
*  Configuration. While wanting the diary app to be configurable for different scenarios, it is also important to keep focused on core function and *not* provide too many hooks. A ``settings.py`` file exists in the diary which provides default values for a few parameters that can be overridden in the project's settings file. For easy discrimination, all configurable parameters have names of the form ``DIARY_XXXXX``. The parameter names will be chosen to be reasonably self-explanatory, and (eventually) will be documented somewhere.
*  Dependencies. Kept to a minimum. They will be documented (promise!).
*  Debate about using a subclass of ``User`` for ``Customer``. It is noted the modern Django approach makes subclassing ``User`` almost *de rigeur*.


Design Considerations
---------------------

Ease of use by end users is paramount, because it is intended the application will be used by people unversed in software. Use of the app needs to be simple and intuitive, even more so than ease of installation and deployment.

Web deployment was decided upon at an early stage, because this enables use of the app from more than one location. The web server may be local or on the internet. One use case I had in mind was being able to check/modify the diary when at home, as well as at work. Web deployment allows customers as well as staff to use the app.

The decision for web deployment, coupled with a preference for Python as the main language, led naturally to using Django as the framework. This also gives flexibility of choice for the database engine, as the Django settings automatically take care of that, provided appropriate Python drivers are installed.

``Django-Calendarium`` was initially chosen as the calendar/diary engine after some consideration of the options available. However, although hooks are available, they were not located in what I regarded as convenient places to do what I wanted to do. I tentatively played with some other calendar/scheduling apps, and reluncantly decided I needed to brew my own to get what I wanted.

I found a tutorial by ``LightBird``. Although the code was terrible and outdated, it gave me a model workflow to follow as I both developed a calendar app and learned Django, JavaScript, CSS, HTML5, and other necessary technologies.

I eventually decided to subclass ``User`` to make a custom user class called ``Customer``. I did that to enable a tight relationship between customers as users and diary entries in the simplest possible way. Other options seemed to involve jumping through too many database join hoops. This may work against reusability of this app, but I think the tweaks I have put into the admin backend (thanks to ``django-model-utils``) may mitigate this. In principle the admin backend in this app should be able to accommodate other custom users, but I may not have given enough attention to that possibility in my own code. It will be interesting to get feedback about that from devs, so keep me posted!

To make the UI fast and intuitive to use, some effort has been put into applying drag-and-drop and modal displays of selected data using ``ajax``. However, most features that involve changes to database content continue to be displayed and updated via conventional ``GET`` and ``POST`` of forms. In this way, an ``Entry`` can be quickly updated with a new time or date by simply dragging it to an appropriate place on the diary grid. Where time is less critical the more robust approach of conventional Django forms takes over.


Testing
-------

To avoid complications with constantly changing dates and times during tests some of the tests of the ``Entry`` functionality make use of ``freezegun``, so that tests that depend on time of day, etc, can be performed reliably and repeatably. After struggling with the Python built-in ``unittest.mock`` suite I found ``freezegun`` super-easy to use (like, one-line-of-code easy) and I recommend it to anyone who needs to test any code that uses or manipulates time-dependent phenomena.

``Freezegun`` introduces some additional dependencies above those needed to run ``django-diary``. These are recorded in ``dev-requirements.txt`` which should be used in place of ``requirements.txt`` for setting up testing and development environments from git clones.


Development Path
----------------

======= ====== ======= =========================================================
Version Python Django  Description
======= ====== ======= =========================================================
<=v0.35 3.4    1.8     Original development versions. EOL.
v0.4    3.8    1.11.29 Base Python 3.8 implementation.
v1.x    3.8    1.11.29 Django 1 bugfix releases. django-model-utils==3.2.0
v2.x    3.8    2.2.13  Django 2 bugfix releases. django-model-utils==4.0.0
v3.x    3.8    3.2.20  Django 3 bugfix releases.
v4.x    3.11   4.2.11  Django 4 bugfix releases.
v5.x    3.11+  5.x     Django 5 development stream (TBA).
======= ====== ======= =========================================================


History And References
----------------------

This started out as a series of experimental projects built on top of Django tutorials, and explorations of existing Django calendar apps, Django snippets and other Django projects on Github:

1. `Django Project Tutorial <https://docs.djangoproject.com/en/1.8/intro/tutorial01/>`_

#. `Django Girls <https://djangogirls.org/>`_

#. `LightBird Calendar Tutorial <http://lightbird.net/dbe/cal1.html>`_

#. `Django Scheduler <https://github.com/llazzaro/django-scheduler>`_

#. `Django Calendarium <https://github.com/bitmazk/django-calendarium>`_

#. `Django User Customisation <http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/>`_

#. `Freezegun <https://github.com/spulec/freezegun/>`_

#. `Django Model Utilities <https://github.com/carljm/django-model-utils>`_
