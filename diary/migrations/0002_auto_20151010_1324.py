# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('diary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='edited',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 10, 10, 12, 24, 48, 619511, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entry',
            name='editor',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL, related_name='edited_entries'),
        ),
    ]
