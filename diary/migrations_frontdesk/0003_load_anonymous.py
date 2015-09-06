# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist


def load_fixture(apps, schema_editor):
    """
    Create an anonymous customer and user. Instead of loading from a fixture
    the database's own tools are used to create and save the necessary objects.
    This works round all sorts of problems with serialisation and seems to be 
    more reliable.
    """
    # check for prior existence, bail-out if found
    customerModel = apps.get_model('diary', 'Customer')
    try:
        anonymousCustomer = customerModel.objects.get(username='anon')
        if anonymousCustomer:
            return
    except ObjectDoesNotExist:
        pass

    # create the anonymous customer by making the object and saving it.
    anonymousCustomer = customerModel.objects.create(
        username='anon',
        # TODO: hard-coded password does not seem like a good idea
        password='pbkdf2_sha256$20000$PPyRHzALIqv2$2oPuuC6ZkvdSCi0XK8S0L5EgoBj01TuHfa9huzvq9pQ=',
        first_name="anonymous",
        last_name="",
        phone="",
    )
    anonymousCustomer.save()


def unload_fixture(apps, schema_editor):
    """
    Try to surgically remove the anonymous customer/user data added by the 
    fixture.
    """

    customerModel = apps.get_model('diary', 'Customer')
    anonymousCustomer = customerModel.objects.get(username='anon')
    anonymousCustomer.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0002_auto_20150720_1757',),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
