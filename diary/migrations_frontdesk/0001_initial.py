# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to=settings.AUTH_USER_MODEL, serialize=False)),
                ('phone', models.CharField(blank=True, null=True, validators=[django.core.validators.RegexValidator(regex='[0-9][0-9 ]+', message='Not a valid phone number')], max_length=20)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
