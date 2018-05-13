# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import Football

def index(request):
    football = Football.objects.all()

    context = {
        'football': football,
    }
    return render(request, 'index.html', context)

