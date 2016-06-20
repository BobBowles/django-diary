from django.shortcuts import (
    get_object_or_404, 
    redirect,
    render, 
    render_to_response,
)
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
import calendar
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.template import RequestContext


# Create your views here.

from .models import Entry, Customer
from .forms import EntryForm
from .admin import CustomerCreationForm, CustomerChangeForm
from . import settings


# set the first day of the week (default 0=monday)
# (uses settings variable DIARY_FIRST_DAY_OF_WEEK)
calendar.setfirstweekday(settings.DIARY_FIRST_DAY_OF_WEEK)


MONTH_NAMES = calendar.month_name[1:]
DAY_NAMES = (
    calendar.day_name[calendar.firstweekday():] + 
    calendar.day_name[:calendar.firstweekday()]
)


# format definitions for the date and time slugs
DATE_SLUG_FORMAT = '%Y-%m-%d'
TIME_SLUG_FORMAT = '%H-%M'
DATETIME_SLUG_FORMAT = '%Y-%m-%d_%H-%M'

# choose 12-hour or 24-hour time display format from meridian settings
TIME_FORMAT = '%I:%M' if settings.DIARY_SHOW_MERIDIAN else '%H:%M'

# entry title date format
ENTRY_DATE_FORMAT = '%a %d %b %Y'



class Statistics(object):
    """
    Wrapper class for Entry statistics.
    """


    def __init__(self, total, cancelled, no_show):
        self.total = total
        self.cancelled = cancelled
        self.no_show = no_show
        self.bookings = total - cancelled - no_show


    def __str__(self):
        return (
            'Bookings: {0}<br />'
            'Cancelled: {1}<br />'
            'No-Shows: {2}<br />'
            'Total: {3}'
        ).format(self.bookings, self.cancelled, self.no_show, self.total)



def get_statistics(entries):
    """
    Derive the statistics for a queryset or list of entries.
    """
    total = len(entries)

    if total:
        cancelled = no_show = 0
        for entry in entries:
            if entry.cancelled: cancelled += 1
            if entry.no_show: no_show += 1
        return Statistics(total, cancelled, no_show)
    else: 
        return None



def evaluateTimeSlots():
    """
    Calculate labels and starting times for diary day display.
    Returns a list of labels and start/end times of time slots.
    """
    DUMMY_DAY = timezone.localtime(timezone.now()).date()

    time = datetime.datetime.combine(DUMMY_DAY, settings.DIARY_MIN_TIME)
    finish = datetime.datetime.combine(DUMMY_DAY, settings.DIARY_MAX_TIME)
    timeSlots = []
    while (time <= finish):
        thisTime = time.time()
        time += settings.DIARY_TIME_INC
        timeSlots.append((
            thisTime.strftime(TIME_FORMAT), 
            thisTime.strftime(TIME_SLUG_FORMAT),
            thisTime,
            time.time(),
        ))
    return timeSlots


TIME_SLOTS = evaluateTimeSlots()


def get_today_now():
    """
    Obtain the current date and time as separate entities.
    """
    today = timezone.localtime(timezone.now()).date()
    now = timezone.localtime(timezone.now()).time()
    return today, now



def reminders(request):
    """
    Data for the reminder sidebar.
    """

    today, now = get_today_now()
    tomorrow = today + datetime.timedelta(days=1)

    user = request.user
    queryset = (                            # customers see their own entries
        Entry.objects.filter(
            Q(date=today, time__gte=now)|Q(date=tomorrow), 
            customer=user, 
            cancelled=False,
        ) if isinstance(user, Customer)
        else Entry.objects.filter(          # admin/staff users see everything
            Q(date=today, time__gte=now)|Q(date=tomorrow), 
        )
    )
    return queryset.order_by('date', 'time')



@login_required
def year(request, year=None):
    """
    List three years per page.
    """

    now = timezone.localtime(timezone.now()).date()
    if year:
        year = int(year)
    else:
        year = now.year

    years = []
    for yr in [year-1, year, year+1,]:
        months = []
        for n, month in enumerate(MONTH_NAMES):
            entries = Entry.objects.filter(date__year=yr, date__month=n+1)
            entry = (True if entries 
                else False)
            current = (True if (yr == now.year) and (n == now.month-1)
                else False)
            months.append({
                'n': n+1,
                'name': month, 
                'entry': entry, 
                'current': current,
                })
        years.append((yr, months))

    return render_to_response(
        'diary/year.html', 
        {
            'years': years,
            'user': request.user,
            'prev_year': year - 3,
            'next_year': year + 3,
            'reminders': reminders(request),
        }, 
        context_instance=RequestContext(request),
    )


@login_required
def month(request, year=None, month=None, change=None):
    """
    Display the days in the specified month.
    """

    # default to this month
    today, now = get_today_now()
    if not year:
        year, month = today.year, today.month
    else:
        year, month = int(year), int(month)
    date = timezone.datetime(year=year, month=month, day=15).date()

    # handle month change, with year rollover
    if change:
        monthDelta = datetime.timedelta(days=31)
        if change == 'prev': 
            monthDelta = datetime.timedelta(days=-31)
        date = date + monthDelta

    # intial values
    cal = calendar.Calendar(calendar.firstweekday())
    month_days = cal.itermonthdays(date.year, date.month)
    weeks = [[]]
    week_no = 0

    # process all the days in the month
    for day in month_days:
        entry_list = statistics = current = None
        nav_slug = None
        if day:
            dayDate = datetime.date(year=date.year, month=date.month, day=day)
            entries = (
                Entry.objects.filter(date=dayDate) if request.user.is_staff
                else Entry.objects.filter(
                    date=dayDate, 
                    customer=request.user,
                    cancelled=False,
                )
            )
            if request.user.is_staff:
                statistics = get_statistics(entries)
            else:
                entry_list = list(entries)

            nav_slug = dayDate.strftime(DATE_SLUG_FORMAT)
            current = (dayDate == today)
        weeks[week_no].append((day, nav_slug, entry_list, statistics, current))
        if len(weeks[week_no]) == 7:
            weeks.append([])
            week_no += 1

    return render_to_response(
        'diary/month.html',
        {
            'date': date,
            'weeks': weeks,
            'month_name': MONTH_NAMES[date.month-1],
            'day_names': DAY_NAMES,
            'reminders': reminders(request),
        }, 
        context_instance=RequestContext(request),
    )


def getDate(year, month, day, change):
    """
    Helper function to obtain the date from kwargs.
    """

    # default to today
    print('DEPRECATED:  Getting kwargs date...')
    today, now = get_today_now()
    if not year:
        year, month, day = today.year, today.month, today.day
    else:
        year, month, day = int(year), int(month), int(day)
    date = timezone.datetime(year=year, month=month, day=day).date()

    # handle day change with year and month rollover
    if change:
        dayDelta = datetime.timedelta(days=1)
        if change == 'prev':
            dayDelta = datetime.timedelta(days=-1)
        date = date + dayDelta
    return date


def getDateFromSlug(slug, change):
    """
    Helper to derive a date from an iso format slug.
    """

    # default to today
    today, now = get_today_now()
    date = None
    if not slug:
        date = today
    else:
        date = datetime.datetime.strptime(slug, DATE_SLUG_FORMAT).date()

    # handle day change with year and month rollover
    if change:
        dayDelta = datetime.timedelta(days=1)
        if change == 'prev':
            dayDelta = datetime.timedelta(days=-1)
        date = date + dayDelta
    return date


def getDatetimeFromSlug(slug):
    """
    Helper method to derive a date and time from a datetime slug.
    """

    date_time = datetime.datetime.strptime(slug, DATETIME_SLUG_FORMAT)
    return date_time.date(), date_time.time()


def evaluateBusinessLogic(day, startTime, endTime):
    """
    Evaluate the booleans that control the display business logic for day and 
    multi-day views.
    """
    today, now = get_today_now()
    current = ((now >= startTime and now < endTime) and day == today)
    trading = (
        startTime >= settings.DIARY_OPENING_TIMES[day.weekday()] and
        endTime <= settings.DIARY_CLOSING_TIMES[day.weekday()]
    ) # trading time
    historic = (
        day < today or (day == today and endTime < now)
    ) # historic data
    booking_allowed_date = (today + 
        datetime.timedelta(days=settings.DIARY_MIN_BOOKING)
    )
    before_advance = day < booking_allowed_date
    allow_dnd = trading and not (historic or before_advance)
    return current, trading, historic, before_advance, allow_dnd


@login_required
def multi_day(request, slug=None, change=None):
    """
    Display entries in a calendar-style 4-day layout.
    """

    date = getDateFromSlug(slug, change)

    # get date information etc for the days to display
    date_slots = []
    dayDelta = datetime.timedelta(days=1)
    for i in range(0, settings.DIARY_MULTI_DAY_NUMBER):
        day = date + i*dayDelta
        dayHeader = day.strftime('%a %d')
        date_slug = day.strftime(DATE_SLUG_FORMAT)
        date_slots.append((
            day,
            dayHeader,
            date_slug,
        ))

    # header information
    date_start_head = date_slots[0][0].strftime('%b %d')
    date_end_head = date_slots[-1][0].strftime('%b %d')
    nav_slug = date_slots[0][0].strftime(DATE_SLUG_FORMAT)

    # obtain the days' entries divided into time slots
    # rows represent times...
    time_slots = []
    for timeLabel, time_slug, startTime, endTime in TIME_SLOTS:
        # cols represent days...
        day_entries = []
        for day, dayHeader, date_slug in date_slots:
            entries = (
                Entry.objects.filter(
                    date=day, 
                    time__gte=startTime, 
                    time__lt=endTime, 
                ) if request.user.is_staff
                else Entry.objects.filter(
                    date=day,
                    time__gte=startTime, 
                    time__lt=endTime, 
                    customer=request.user,
                    cancelled=False,
                )
            ).order_by('time')

            # evaluate the business rules for entry booking
            current, trading_time, historic, before_advance, allow_dnd =\
                evaluateBusinessLogic(day, startTime, endTime)

            day_entries.append((
                '_'.join((date_slug, time_slug)), # date-time slug
                entries, # the entries
                current, # now
                trading_time, # trading time
                historic, # historic data
                before_advance, # before advance booking threshold
                allow_dnd, # allow drag-n-drop
            ))
        time_slots.append((
            timeLabel, 
            startTime,
            day_entries,
        ))

    return render_to_response(
        'diary/multi_day.html', 
        {
            'date': date,
            'n_cols': settings.DIARY_MULTI_DAY_NUMBER,
            'date_start_head': date_start_head,
            'date_end_head': date_end_head,
            'nav_slug': nav_slug,
            'user': request.user,
            'month_name': MONTH_NAMES[date.month-1],
            'time_slots': time_slots,
            'date_slots': date_slots,
            'reminders': reminders(request),
        }, 
        context_instance=RequestContext(request),
    )


@login_required
def day(request, slug=None, change=None):
    """
    Display entries in a particular day in a calendar-style day view.
    """

    date = getDateFromSlug(slug, change)
    date_slug = date.strftime(DATE_SLUG_FORMAT)

    # obtain the day's entries divided into time slots
    time_slots = []
    for timeLabel, time_slug, startTime, endTime in TIME_SLOTS:
        entries = (
            Entry.objects.filter(
                date=date, 
                time__gte=startTime, 
                time__lt=endTime,
            ) if request.user.is_staff
            else Entry.objects.filter(
                date=date, 
                time__gte=startTime, 
                time__lt=endTime, 
                customer=request.user,
                cancelled=False,
            )
        ).order_by('time')

        # evaluate the business rules for entry booking
        current, trading_time, historic, before_advance, allow_dnd =\
            evaluateBusinessLogic(date, startTime, endTime)

        time_slots.append((
            timeLabel, 
            '_'.join((date_slug, time_slug)),
            startTime,
            entries,
            current, # flag now
            trading_time, # trading 
            historic, # historic data
            before_advance, # advance booking prohibited
            allow_dnd,
        ))

    return render_to_response(
        'diary/day.html', 
        {
            'date': date,
            'nav_slug': date_slug,
            'user': request.user,
            'month_name': MONTH_NAMES[date.month-1],
            'time_slots': time_slots,
            'reminders': reminders(request),
        }, 
        context_instance=RequestContext(request),
    )


def get_redirect_url(request, default):
    """
    Utility to derive the correct url for redirections.
    
    The url to be used is obtained from the request's GET dict, which gets it 
    from the clicked template link via the '?next=' parameter.
    
    A default url must be specified for use in the event of failure.
    """

    next_url_bits = request.GET.get(
        'next',                             # use specified redirect if exists
        default,                            # 'safe' fallback
    ).split('/')
    date_index = next_url_bits.index('diary') + 2

    if not next_url_bits[date_index]:       # no date, so assume today
        return '/'.join(x for x in next_url_bits)

    if not next_url_bits[date_index+1]:     # no change component, pass as-is
        return '/'.join(x for x in next_url_bits)

    # deal with change component by re-calculating the date slug
    slug = getDateFromSlug(
        next_url_bits[date_index], 
        next_url_bits[date_index+1],
    ).strftime(DATE_SLUG_FORMAT)

    # return the unchanged prefix plus the new date slug
    return '/'.join(x for x in next_url_bits[:date_index]) + '/' + slug + '/'


@login_required
def entry(request, pk=None, slug=None, customer_pk=None):
    """
    Edit/create an entry for the diary.
    """

    # defaults are here and now if no date/time is provided
    today, now = get_today_now()
    entry = None

    # determine the navigation context for redirection
    next_url = get_redirect_url(request, reverse('diary:home'))
    #print('Entry: next_url is {0}'.format(next_url))

    # decide whether we are creating a new entry or editing a new one
    if pk:                              # edit existing entry
        entry = get_object_or_404(Entry, pk=pk)
    else:                               # make a new entry
        # determine the date and time to use
        if slug:
            date, time = getDatetimeFromSlug(slug)
        entry = Entry(
            date=date,
            time=time,
            creator=request.user,
            customer=(
                request.user if not request.user.is_staff
                else None
            ),
        )
    entry.editor = request.user

    # if a customer pk is specified set it as the customer
    if customer_pk:
        customer = get_object_or_404(Customer, pk=customer_pk)
        entry.customer = customer

    exclude_customer = not request.user.is_staff
    form = EntryForm(
        request.POST or None, 
        instance=entry, 
        exclude_customer=exclude_customer
    )
    if form.is_valid():
        entry = form.save(commit=False)
        entry.save()
        return redirect(next_url)

    # have to set up the customer widget after form creation
    if not exclude_customer:
        related_url = related_kwargs = None
        if pk:
            related_url = 'diary:customer_add_entry_pk'
            related_kwargs = {
                'entry_pk': pk,
            }
        elif slug:
            related_url = 'diary:customer_add_entry_slug'
            related_kwargs = {
                'entry_slug': slug,
            }
        else:
            related_url = 'diary:customer_add'
        form.fields['customer'].widget.related_url = related_url
        form.fields['customer'].widget.related_kwargs = related_kwargs

    context = {
        'form': form,
        'date': entry.date.strftime(ENTRY_DATE_FORMAT),
        'return_nav': next_url,
        'return_nav_prev': next_url+'prev/',
        'return_nav_next': next_url+'next/',
        'reminders': reminders(request),
    }
    return render_to_response(
        'diary/entry.html', 
        context, 
        context_instance=RequestContext(request),
    )


@login_required
def entry_update(request):
    """
    Update an entry's details via ajax. 
    At present only the date and time can be changed this way.
    """

    pk = request.POST['pk']
    #print('pk is {0}'.format(pk))
    entry = get_object_or_404(Entry, pk=pk)
    entry.editor = request.user

    datetime_slug = request.POST['slug']
    #print('datetime_slug is {0}'.format(datetime_slug))
    date, time = getDatetimeFromSlug(datetime_slug)

    # try updating the entry
    entry.date = date
    entry.time = time

    # clear admin status flags if set
    entry.no_show = False
    entry.cancelled = False

    try:
        entry.save()
    except ValidationError as ve:
        # attempt to fit the entry in later in the time slot
        endTime = (
            datetime.datetime.combine(date, time) + TIME_INC
            ).time()
        otherEntry = Entry.objects\
            .filter(
                date=date, 
                time__gte=time, 
                time__lt=endTime, 
            ).first()
        if otherEntry.time_end() >= endTime:
            # really no more space in this time slot
            raise ve
        # try adding after the other entry
        entry.time = otherEntry.time_end()
        entry.save()

    message = 'Date / time changed to {0}, {1}'.format(entry.date, entry.time)
    data = {'message': message}
    #print('Sending entry_update data {0}'.format(data))
    return JsonResponse(data)


@login_required
def entry_modal(request, pk):
    """
    Prepare and send an html snippet to display an entry in a modal dialog via
    ajax - but using html.
    """

    # obtain redirection information from the request
    redirect_url = request.GET.get('redirect_url', reverse('diary:day_now'))

    entry = get_object_or_404(Entry, pk=pk)

    # decide if the modal's delete/edit buttons should be enabled/visible
    today, now = get_today_now()
    enable_edit_buttons = False
    enable_no_show_button = False

    # avoid infinite recursion if this is for a popup on history view.
    enable_history_button = not 'history' in redirect_url

    # initial book-ahead date hard-coded to 7 days in advance of chosen entry
    book_ahead_date = entry.date + datetime.timedelta(days=7)
    book_ahead_datetime_slug = datetime.datetime.combine(
        book_ahead_date, 
        entry.time,
    ).strftime(DATETIME_SLUG_FORMAT)

    if request.user.is_staff:
        enable_edit_buttons = True
        enable_no_show_button = (
            not entry.no_show and
            (entry.date < today or (entry.date == today and entry.time < now))
        )
    else:
        booking_threshold = (
            today + datetime.timedelta(days=settings.DIARY_MIN_BOOKING)
        )
        if (
            entry.date == today and 
            booking_threshold == today and 
            entry.time > now
        ):
            enable_edit_buttons = True
        elif booking_threshold > today and entry.date >= booking_threshold:
            enable_edit_buttons = True

    html = render_to_string(
        'diary/modal_entry.html',
        context={
            'entry': entry,
            'redirect_url': redirect_url,
            'enable_edit_buttons': enable_edit_buttons,
            'enable_no_show_button': enable_no_show_button,
            'enable_history_button': enable_history_button,
            'book_ahead_datetime_slug': book_ahead_datetime_slug,
        },
        request=request,
    )
    #print('Sending entry_modal data {0}'.format(html))
    return HttpResponse(html)


@login_required
def entry_admin(request, pk, action):
    """
    Deal with a diary entry's administrative status.
    
    action is one of:
    delete          delete the entry - remove it from the database
    cancel          mark the entry as cancelled
    no_show         mark the entry as a no-show
    """

    redirect_url = get_redirect_url(request, reverse('diary:day_now'))
    entry = get_object_or_404(Entry, pk=pk)
    date = entry.date

    if action == 'delete':
        entry.delete()
    else:
        entry.cancelled = (action == 'cancel')
        entry.no_show = (action == 'no_show')
        entry.editor = request.user
        entry.save()

    return redirect(
        redirect_url, 
        slug=date.strftime(DATE_SLUG_FORMAT),
    )


def customer_add(request, entry_pk=None, entry_slug=None):
    """
    Customer creation.
    
    The entry_pk and entry_slug give ways to redirect to the entry form where
    this method was invoked.
    """

    form = CustomerCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        if entry_pk:
            return HttpResponseRedirect(
                reverse(
                    'diary:entry_customer', 
                    kwargs={
                        'pk': entry_pk,
                        'customer_pk': form.instance.pk,
                    },
                )
            )
        elif entry_slug:
            return HttpResponseRedirect(
                reverse(
                    'diary:entry_new_customer',
                    kwargs={
                        'slug': entry_slug,
                        'customer_pk': form.instance.pk,
                    }
                )
            )
        elif not request.user.is_authenticated():
            return HttpResponseRedirect(
                reverse('django.contrib.auth.views.login')
            )
        else:
            return HttpResponseRedirect(
                reverse('diary:entry')
            )

    context = {
        'form': form,
        'entry_pk': entry_pk,
        'entry_slug': entry_slug,
        'reminders': reminders(request),
    }
    return render_to_response(
        'diary/customer_add.html', 
        context, 
        context_instance=RequestContext(request),
    )


def get_customer_and_redirect(request, pk):
    """
    Utility to derive the customer and redirect url to use.
    
    Only allow pk different from user if user is staff.
    If no pk is specified the current logged-on user is assumed.
    If no url is found diary:home is used as default/fallback.
    """

    customer = (
        Customer.objects.get(pk=pk) if (pk and request.user.is_staff) 
        else request.user
    )

    redirect_url = (
        request.GET['next'] if 'next' in request.GET 
        else reverse('diary:home')
    )

    return customer, redirect_url



@login_required
def customer_change(request, pk):
    """
    Change the specified customer's personal details.
    """

    customer, redirect_url = get_customer_and_redirect(request, pk)

    form = CustomerChangeForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect(redirect_url)

    context = {
        'form': form,
        'next': redirect_url,
        'customer': customer,
        'reminders': reminders(request),
    }
    return render_to_response(
        'diary/customer_change.html', 
        context, 
        context_instance=RequestContext(request),
    )


@login_required
def history(request, pk):
    """
    Review a customer's treatment history.
    """

    customer, redirect_url = get_customer_and_redirect(request, pk)

    # get the relevant entries
    today, now = get_today_now()
    entries = list(
        Entry.objects.filter(
            customer=customer,
            date__lte=today,
        ).order_by('date', 'time')
    )

    # some arithmetic 
    statistics = get_statistics(entries)

    context = {
        'next': redirect_url,
        'customer': customer,
        'entries': entries,
        'statistics': statistics,
        'reminders': reminders(request),
    }
    return render_to_response(
        'diary/history.html', 
        context, 
        context_instance=RequestContext(request),
    )

