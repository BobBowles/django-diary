# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import datetime
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
                ('user_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, to=settings.AUTH_USER_MODEL, primary_key=True)),
                ('phone', models.CharField(max_length=20, blank=True, validators=[django.core.validators.RegexValidator(message='Not a valid phone number', regex='[0-9][0-9 ]+')], null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(max_length=1, default='F', choices=[('M', 'Male'), ('F', 'Female')])),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
            bases=('auth.user',),
            managers=[
                ('objects', diary.models.CustomerManager()),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date', models.DateField()),
                ('time', models.TimeField(default=datetime.time(12, 0))),
                ('duration', models.TimeField(blank=True, default=datetime.time(1, 0))),
                ('notes', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(blank=True, null=True, related_name='created_entries', to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(blank=True, null=True, related_name='entries', to='diary.Customer')),
            ],
            options={
                'verbose_name_plural': 'entries',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('min_duration', models.DurationField(blank=True)),
                ('resource_required', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='resource',
            field=models.ForeignKey(blank=True, null=True, to='diary.Resource'),
        ),
        migrations.AddField(
            model_name='entry',
            name='treatment',
            field=models.ForeignKey(blank=True, null=True, to='diary.Treatment'),
        ),
    ]
