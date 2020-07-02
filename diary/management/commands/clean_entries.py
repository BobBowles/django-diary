from django.core.management.base import BaseCommand, CommandError
from diary.models import Entry, Customer
from diary.views import get_today_now
import datetime


class Command(BaseCommand):
    """
    Periodically clean out old database data in the Entry table.
    """

    help = "Clean old Entry data in the database."


    def add_arguments(self, parser):
        """
        Define the date before when to delete entries either by
        -a --age      age of the entry (from the date of the appointment)
        -b --before   date before which to delete
        """
        parser.add_argument(
            '-a',
            '--age',
            help="age in years",
            type=int,
            default=0,
        )
        parser.add_argument(
            '-b',
            '--before',
            help="date HWM (yyyy-mm-dd)",
            type=datetime.date.fromisoformat,
            default=get_today_now()[0],
        )


    def handle(self, *args, **kwargs):
        """
        Implement the database cleanout using the argument(s) provided.
        """

        today, now = get_today_now()

        age = kwargs['age']
        before = kwargs['before']

        # override before date with date calculated from age
        if age > 0:
            before = today.replace(year=today.year-age)

        # ensure the date being asked for is sane
        if not before or before >= today:
            raise CommandError("Specify a valid before date (-b) or an age (-a).")

        # delete entries before the selected date
        entries = Entry.objects.filter(date__lt=before,)
        n = len(entries)
        name = 'entry' if n==1 else 'entries'   # pluralisation
        if kwargs['age']:
            print(f"Cleaning {n} {name} older than {age} years ... ", end='')
        else:
            print(f"Cleaning {n} {name} prior to {before} ... ", end='')
        entries.delete()
        print("Done")
