# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def select_title(apps, schema_editor):
    """
    Select (hopefully) appropriate titles for existing customer data.
    """
    # gender options
    MALE = 'M'
    FEMALE = 'F'

    # title options
    MR = 'MR'
    MRS = 'MRS'
    MISS = 'MISS'
    MS = 'MS'
    DR = 'DR'
    PROF = 'PROF'
    REV = 'REV'
    TITLE_CHOICES = {
        MR: 'Mr',
        MRS: 'Mrs',
        MISS: 'Miss',
        MS: 'Ms',
        DR: 'Dr',
        PROF: 'Prof',
        REV: 'Rev',
    }

    Customer = apps.get_model('diary', 'Customer')
    for customer in Customer.objects.all():

        # is there a clue in the customer first name field?
        if customer.first_name in TITLE_CHOICES:
            customer.title = TITLE_CHOICES.keys()[
                TITLE_CHOICES.values().index(customer.first_name)
            ]
            customer.first_name = ''

        # no clues so fall back to gender stereotypes where possible
        elif customer.gender:
            customer.title = MR if customer.gender == MALE else MRS

        customer.save()



class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0004_customer_title'),
    ]

    operations = [
        migrations.RunPython(select_title),
    ]
