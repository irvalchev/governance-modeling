
"""
Definition of urls for the app.
"""

from django.conf.urls import  url
import app.views

urlpatterns = [url(r'^execute', app.views.test, name='execute')]
