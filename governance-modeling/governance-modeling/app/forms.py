"""
Definition of forms.
"""

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from app.models import ParameterValue, ProjectRequirementCondition

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class ProjectRequirementConditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectRequirementConditionForm, self).__init__(*args, **kwargs)
        try:
            condition_param = self.instance.condition_parameter
            self.fields['parameter_value'].queryset = ParameterValue.objects \
                .filter(parameter=condition_param)
        except ObjectDoesNotExist:
             self.fields['parameter_value'].queryset = \
                ParameterValue.objects.filter(parameter=None)
        
