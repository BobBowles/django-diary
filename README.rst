Django Diary
============


Description
-----------

Django-Diary is a project to create an easy-to-use desk diary and scheduling tool for use in a fast-paced retail environment. The aim is to be able to schedule and manage client bookings with available resources as quickly and easily as possible with no fuss.


The Models
----------

The diary model has deliberately been made very simple. It is built on the foundation of practical experience manning the front desk of a health clinic. It needs to be easy and fast to use.

The core concept is a diary 'entry', which records the date and time of an appointment with a 'customer', which may use a time-allocated 'resource'. The 'duration' of each booking is determined by the type of 'treatment' to be administered.

There are no repeating entries; while it is expected that customers will make repeat bookings, it is assumed the repeat bookings will _not_ follow any simple rule. So, to avoid complexity that will not actually be useful, all diary entries are considered as unique and unrelated occurrences. This is in stark contrast to popular (and very fine) calendar/scheduling apps like django-schedule and django-calendarium.

Entries are allowed to overlap in time, provided there are no resource conflicts. If a resource is assigned to an entry, no other entry can use the same resource at the same time.

Customers may be users of the system, but they have additional attributes. In keeping with the health clinic paradigm, they have demographic and health-related information associated with them, contact details, and of course their treatment history, which can be derived from their historical record of appointments.

In the interests of confidentiality, customers may only see and alter their own details and appointments. Staff members are able to see and alter the details of all entries.


Reusability
-----------

At this early stage reusability is an aspiration rather than a reality. To achieve this the following considerations have been/need to be made:

*  Overriding of templates and styles. A main_base.html template is to be constructed that forms the basis of a working example of the app, and at the same time provides a starting point for overriding. Attention also needs to be given to navigation hooks.
*  Configuration. While wanting the diary app to be configurable for different scenarios, it is also important to keep focused on core function and _not_ provide too many hooks. A settings.py file exists in the diary which provides default values for a few parameters that can be overridden in the project's settings file. For easy discrimination, all configurable parameters have names of the form DIARY_XXXXX. The parameter names will be chosen to be reasonably self-explanatory, and (eventually) will be documented somewhere.


Design Considerations
---------------------

Ease of use is paramount, because it is intended the application will be used by people unversed in software. Use of the app needs to be simple and intuitive.

Web deployment was decided upon at an early stage, because this enables use of the app from more than one location. The web server may be local or on the internet. One use case I had in mind was being able to check/modify the diary when at home, as well as at work.

The decision for web deployment, coupled with a preference for Python as the main language, led naturally to using Django as the framework. This also gives flexibility of choice for the database engine, as the Django settings will automatically take care of that, provided appropriate Python drivers are installed.

Django-Calendarium was ititially chosen as the calendar/diary engine after some consideration of the options available. However, although hooks are available, they were not located in what I regarded as convenient places to do what I wanted to do. I tentatively played with some other calendar/scheduling apps, and reluncantly decided I needed to brew my own to get what I wanted.

I found a tutorial by LightBird. Although the code was terrible and outdated, it gave me a model workflow to follow as I both developed a calendar app and learned Django, JavaScript, CSS, HTML5, and other necessary technologies.


History
-------

This started out as a series of experimental projects built on top of Django tutorials.


