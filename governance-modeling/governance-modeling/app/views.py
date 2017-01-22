"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.forms import ExecuteForm

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        form = ExecuteForm(request.POST)
        if form.is_valid():
            param_values = list(form.param_values())
            return render(
                request,
                'app/index.html',
                {
                    'title':'Result',
                    "param_values": param_values
                }
            )
    else:
        form = ExecuteForm()

    return render(
        request,
        'app/index.html',
        {
            'title':'Home',
            "execute_form": form
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