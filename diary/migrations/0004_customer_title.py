# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0003_auto_20151010_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='title',
            field=models.CharField(default='MRS', max_length=4, choices=[('MR', 'Mr'), ('MRS', 'Mrs'), ('MISS', 'Miss'), ('MS', 'Ms'), ('DR', 'Dr'), ('PROF', 'Prof'), ('REV', 'Rev')]),
        ),
    ]
