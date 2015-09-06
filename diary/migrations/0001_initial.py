# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators
import diary.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(to=settings.AUTH_USER_MODEL, parent_link=True, serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Not a valid phone number', regex='[0-9][0-9 ]+')], blank=True, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Customers',
                'verbose_name': 'Customer',
            },
            bases=('auth.user',),
            managers=[
                ('objects', diary.models.CustomerManager()),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=40)),
                ('snippet', models.CharField(max_length=150, blank=True)),
                ('body', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField(blank=True)),
                ('time', models.TimeField(blank=True, default=datetime.time(12, 0))),
                ('duration', models.TimeField(blank=True, default=datetime.time(1, 0))),
                ('remind', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'entries',
            },
        ),
    ]
