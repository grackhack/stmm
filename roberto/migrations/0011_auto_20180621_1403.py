# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roberto', '0010_eventgame_dog'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventgame',
            name='stat_away',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='eventgame',
            name='stat_home',
            field=models.TextField(default=''),
        ),
    ]
