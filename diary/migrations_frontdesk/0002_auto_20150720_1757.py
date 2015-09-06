# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import diary.models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Customer', 'verbose_name_plural': 'Customers'},
        ),
        migrations.AlterModelManagers(
            name='customer',
            managers=[
                ('objects', diary.models.CustomerManager()),
            ],
        ),
    ]
