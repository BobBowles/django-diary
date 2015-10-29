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
        print('Selecting Entries ...')
        today, now = get_today_now()
        tomorrow = today + datetime.timedelta(days=1)
        entries = Entry.objects.filter(
            date=tomorrow,
            customer__email__gt='', # test for non-blank (not non-null) email
        )
        print('Selected {0} Entries:'.format(entries.count()))
#        for entry in entries:
#            print('Customer {0}, email {1}'.format(
#                entry.customer, 
#                entry.customer.email,
#            ))

        # prepare the messages
        print('Preparing messages ...')
        reminder_messages = []
        for entry in entries:
            message = (
                settings.DIARY_SITE_NAME+': Appointment Reminder',
                render_to_string(
                    'diary/email_reminder.txt',
                    context={
                        'entry': entry,
                        'site_name': settings.DIARY_SITE_NAME,
                    },
                ),
                main_settings.DEFAULT_FROM_EMAIL,
                [entry.customer.email],
            )
#            print(
#                'Message: \n'
#                'From: {2}\n'
#                'To: {3}\n'
#                'Subject: {0}\n'
#                'Body:\n{1}'.format(
#                    message[0], # subject
#                    message[1], # body
#                    message[2], # from
#                    message[3], # to
#                )
#            )
            reminder_messages.append(message)

        # send the messages
        print('Sending reminders ...')
        mail.send_mass_mail(reminder_messages, fail_silently=False)
        print('Reminders sent: {0}'.format(len(reminder_messages)))

