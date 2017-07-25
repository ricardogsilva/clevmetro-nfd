# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-25 10:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20170725_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='occurrencenaturalarea',
            name='observation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.OccurrenceObservation'),
        ),
        migrations.AlterField(
            model_name='occurrencetaxon',
            name='observation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.OccurrenceObservation'),
        ),
    ]