# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from .models import Football

def index(request):
    football = Football.objects.all()

    context = {
        'football': football,

    }

    return render(request, 'index.html', context)

