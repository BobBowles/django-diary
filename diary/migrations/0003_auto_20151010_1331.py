# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_editor(apps, schema_editor):
    """
    Add an editor to existing entries.
    
    We choose the customer if it exists, or the creator if it does not.
    """
    Entry = apps.get_model('diary', 'Entry')
    for entry in Entry.objects.all():
        entry.editor = entry.customer if entry.customer else entry.creator
        entry.save()



class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0002_auto_20151010_1324'),
    ]

    operations = [
        migrations.RunPython(add_editor),
    ]
