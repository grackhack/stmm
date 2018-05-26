# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Football(models.Model):
    html_link = models.CharField(default='', null=False, max_length=16)
    begin_time = models.CharField(default='', null=False, max_length=16)
    timer = models.CharField(default='', null=False, max_length=16)
    team_home = models.CharField(default='', null=False, max_length=32)
    rhcard = models.CharField(default='', null=False, max_length=8)
    score = models.CharField(default='', null=False, max_length=32)
    team_away = models.CharField(default='', null=False, max_length=32)
    racard = models.CharField(default='', null=False, max_length=8)
    part_top = models.CharField(default='', null=False, max_length=32)
    league = models.ForeignKey('League', default=None)

    class Meta:
        db_table = 'soccer'


class Country(models.Model):
    caption = models.CharField(default='', null=False, max_length=32)

    class Meta:
        db_table = 'country'


class League(models.Model):
    html_link = models.CharField(default='', null=False, max_length=16)
    caption = models.CharField(default='', null=False, max_length=64)
    country = models.CharField(default='', null=False, max_length=64)

    class Meta:
        db_table = 'league'


class EventGame(models.Model):
    begin_time = models.CharField(default='', null=False, max_length=16)
    timer = models.CharField(default='', null=False, max_length=16)
    team_home = models.CharField(default='', null=False, max_length=32)
    rhcard = models.CharField(default='', null=False, max_length=8)
    score = models.CharField(default='', null=False, max_length=32)
    team_away = models.CharField(default='', null=False, max_length=32)
    racard = models.CharField(default='', null=False, max_length=8)
    part_top = models.CharField(default='', null=False, max_length=32)
    html_link = models.CharField(default='', null=False, max_length=16)
    time_stamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(default='', null=False, max_length=32)
    pre_p1 = models.CharField(default='', null=False, max_length=8)
    pre_x = models.CharField(default='', null=False, max_length=8)
    pre_p2 = models.CharField(default='', null=False, max_length=8)
    live_p1 = models.CharField(default='', null=False, max_length=8)
    live_x = models.CharField(default='', null=False, max_length=8)
    live_p2 = models.CharField(default='', null=False, max_length=8)
    dog = models.CharField(default='', null=False, max_length=2)


    class Meta:
        db_table = 'event_game'


class EventParams(models.Model):
    event_id = models.ForeignKey('EventGame')
    time_stamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(default='', null=False, max_length=32)
    html_link = models.CharField(default='', null=False, max_length=16)

    class Meta:
        db_table = 'event_params'

