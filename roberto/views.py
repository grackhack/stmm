# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import operator
from functools import reduce

from django.shortcuts import render
from django.db.models import Q

from .models import Football, EventGame

def _gen_query():
    cur_time = datetime.datetime.now()
    h1 = str(cur_time.hour) + ':'
    h2 = str((cur_time - datetime.timedelta(hours=1)).hour) + ':'
    h3 = str((cur_time - datetime.timedelta(hours=2)).hour) + ':'
    query = reduce(operator.or_, (Q(timer__iregex=r'[\d+]|перер', begin_time__contains=x) for x in [h1, h2, h3]))
    return query


def index(request):
    games = Football.objects.filter(_gen_query())
    count_live = games.count()
    event = EventGame.objects.filter(_gen_query()).order_by('-begin_time')
    count_event = event.count()
    context = {
        'count_live': count_live,
        'count_event': count_event,
    }
    return render(request, 'index.html', context)


def live_table(request):
    games = Football.objects.filter(_gen_query()).order_by('-begin_time')

    count_live = games.count()
    hour = datetime.datetime.now().hour

    context = {
        'count_live': count_live,
        'games': games
    }

    return render(request, 'live_table.html', context)


def event_table(request):
    games = EventGame.objects.filter(_gen_query()).order_by( '-time_stamp','-begin_time', 'html_link')
    count_event = games.count()

    context = {
        'count_event': count_event,
        'games': games
    }

    return render(request, 'event_table.html', context)
