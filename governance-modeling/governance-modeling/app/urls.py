
"""
Definition of urls for the app.
"""

from django.conf.urls import  url
import app.views

urlpatterns = [url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about', app.views.about, name='about')]
