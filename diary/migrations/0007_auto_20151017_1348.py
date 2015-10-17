# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_cancelled(apps, schema_editor):
    """
    Detect entries that have been manually marked as cancelled in the notes and
    toggle their cancelled status to true.
    """

    Entry = apps.get_model('diary', 'Entry')
    for entry in Entry.objects.filter(notes__contains='CANCELLED'):
        entry.cancelled = True
        entry.save()


def update_no_show(apps, schema_editor):
    """
    Detect entries that have been manually marked as no-shows in the notes and
    toggle their no_show status to true.
    """

    Entry = apps.get_model('diary', 'Entry')
    for entry in Entry.objects.filter(notes__contains='NO-SHOW'):
        entry.no_show = True
        entry.save()



class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0006_auto_20151017_1347'),
    ]

    operations = [
        migrations.RunPython(update_cancelled),
        migrations.RunPython(update_no_show),
    ]
