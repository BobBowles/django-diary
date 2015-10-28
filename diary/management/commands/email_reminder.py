from django.core.management.base import BaseCommand, CommandError
from diary.models import Entry, Customer
from diary.views import get_today_now
import datetime
from django.core import mail
from django.template.loader import render_to_string
from django.template import Context
from django.conf import settings



class Command(BaseCommand):
    """
    Command to implement email reminders.
    """


    def handle(self, *args, **kwargs):
        """
        Handler to prepare and submit the emails.
        """
        print('email_reminder Hello World!')

        # select the entries that qualify for reminders
        # TODO: parameterize this - time ahead of today - window width
        print('Select Entries goes here...')
        today, now = get_today_now()
        tomorrow = today + datetime.timedelta(days=1)
        entries = Entry.objects.filter(
            date=tomorrow,
            customer__email__isnull=False,
        )
        for entry in entries:
            print('Entry customer {0}, email {1}'.format(
                entry.customer, 
                entry.customer.email,
            ))

        # prepare the messages
        print('Prepare messages goes here...')
        reminder_messages = []
        for entry in entries:
            message = (
                'Apointment Reminder',
                render_to_string(
                    'diary/email_reminder.txt',
                    context={'entry': entry},
                ),
                settings.DEFAULT_FROM_EMAIL,
                [entry.customer.email],
            )
            print(
                'Message: \n'
                'From: {2}\n'
                'To: {3}\n'
                'Subject: {0}\n'
                'Body:\n{1}'.format(
                    message[0], 
                    message[1], 
                    message[2],
                    message[3],
                )
            )
            reminder_messages.append(message)

        # send the messages
        print('Send messages goes here...')
        mail.send_mass_mail(reminder_messages, fail_silently=False)
