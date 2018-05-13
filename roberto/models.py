# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Football(models.Model):
    begin_time = models.CharField(default='', null=False, max_length=16)
    timer = models.CharField(default='', null=False, max_length=16)
    team_home = models.CharField(default='', null=False, max_length=32)
    hcard = models.CharField(default='', null=False, max_length=8)
    score = models.CharField(default='', null=False, max_length=32)
    team_away = models.CharField(default='', null=False, max_length=32)
    acard = models.CharField(default='', null=False, max_length=8)
    squad = models.CharField(default='', null=False, max_length=32)

    class Meta:
        db_table = 'Football'