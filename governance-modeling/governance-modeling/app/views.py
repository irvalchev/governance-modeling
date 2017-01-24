"""
Definition of views.
"""
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from app.forms import ExecuteForm
from app.dss import retrieve_governance_processes, governance_tree_builder

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        form = ExecuteForm(request.POST)
        if form.is_valid():
            param_values = form.param_values()
            active_requirements = retrieve_governance_processes.get_active_requirements(param_values)
            req_items = retrieve_governance_processes.get_requirement_items(active_requirements)
            
            tb = governance_tree_builder.GovernanceTreeBuilder()
            tree_string = tb.pretty_print_items_support([i.id for i in req_items["condition_items"]])
            return render(
                request,
                'app/index.html',
                {
                    'title':'Result',
                    "tree_string": tree_string
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