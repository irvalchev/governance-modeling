"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home'
        }
    )

def test(request):
    """Renders the test page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/test.html',
        {
            'title':'Test'
        }
    )