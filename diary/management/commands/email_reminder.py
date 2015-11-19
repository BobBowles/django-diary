from django.core.management.base import BaseCommand, CommandError
from diary.models import Entry, Customer
from diary.views import get_today_now
import datetime
from django.core import mail
from django.template.loader import render_to_string
from django.template import Context
from django.conf import settings as main_settings
from diary import settings as settings



class Command(BaseCommand):
    """
    Command to implement email reminders.
    """


    def handle(self, *args, **kwargs):
        """
        Handler to prepare and submit the emails.
        """

        # select the entries that qualify for reminders
        # TODO: currently hard-coded to remind the day before
        today, now = get_today_now()
        tomorrow = today + datetime.timedelta(days=1)
        entries = Entry.objects.filter(
            date=tomorrow,
            cancelled=False, # reminders not needed for cancelled entries
            customer__email__gt='', # test for non-blank (not non-null) email
        ).order_by('time')

        # collect summary info for site admins
        n_emails = entries.count()
        summary = []
        for entry in entries:
            summary.append(
                '{0} <{1}>: {2} {3}:  {4}'.format(
                    entry.customer, 
                    entry.customer.email,
                    entry.date,
                    entry.time,
                    entry.treatment,
                )
            )

        # prepare the messages
        reminder_messages = []
        for entry in entries:
            message = (
                settings.DIARY_SITE_NAME+': Appointment Reminder',
                render_to_string(
                    'diary/email_reminder.txt',
                    context={
                        'entry': entry,
                        'site_name': settings.DIARY_SITE_NAME,
                        'contact_email': main_settings.DEFAULT_FROM_EMAIL,
                        'contact_phone': settings.DIARY_CONTACT_PHONE,
                    },
                ),
                main_settings.DEFAULT_FROM_EMAIL,
                [entry.customer.email],
            )
            reminder_messages.append(message)

        # add a message to notify site admins
        admin_message = 'Reminders sent to {0} customers:\n\n'.format(n_emails)
        admin_message += '\n'.join(summary)
        reminder_messages.append(
            (
                settings.DIARY_SITE_NAME +
                    ': Reminders Summary for {0} at {1}'.format(today, now),
                admin_message,
                main_settings.SERVER_EMAIL,
                [email for name, email in main_settings.ADMINS],
            )
        )

        # send the messages
        mail.send_mass_mail(reminder_messages, fail_silently=False)
        print('Reminder messages sent: {0}'.format(len(reminder_messages)))

