from django.core.management.base import BaseCommand, CommandError



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
        

        # prepare the messages
        print('Prepare messages goes here...')

        # send the messages
        print('Send messages goes here...')
