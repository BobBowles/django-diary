# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0005_auto_20151017_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='entry',
            name='no_show',
            field=models.BooleanField(default=False),
        ),
    ]
