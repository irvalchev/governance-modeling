"""
Definition of forms.
"""

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from app.models import ProjectParameter, ParameterValue, ProjectRequirementCondition

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
            self.fields['allowed_values'].queryset = ParameterValue.objects \
                .filter(parameter=condition_param)
        except ObjectDoesNotExist:
             self.fields['allowed_values'].queryset = \
                ParameterValue.objects.filter(parameter=None)

class ExecuteForm(forms.Form):
    """
    Main form for executing the tool
    """

    def __init__(self, *args, **kwargs):
        params = ProjectParameter.objects.all().prefetch_related('values')
        super(ExecuteForm, self).__init__(*args, **kwargs)

        for param in params:
            field_name = 'param_%s' % param.id
            if param.type == ProjectParameter.BOOLEAN:
                self.fields[field_name] = \
                    forms.BooleanField(label=param.name, required=False)
            elif param.type == ProjectParameter.NUMBER:
                self.fields[field_name] = \
                    forms.DecimalField(label=param.name, required=False)
            elif param.type == ProjectParameter.STRING:
                self.fields[field_name] = \
                    forms.CharField(label=param.name, required=False, max_length=100)
            elif param.type == ProjectParameter.ENUM:
                self.fields[field_name] = \
                    forms.ChoiceField(label=param.name, 
                        required=False,
                        choices=[(0,"")] + [(v.id, v.name) for v in param.values.all()])
            # setting the default bootstrap class for all fields
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def param_values(self):
        """
        Finds the selected parameter values in the form
        Returns a dictionary with keys the id of the parameters
        and value - the selected value
        """
        selected_values = {}
        for name, value in self.cleaned_data.items():
            if name.startswith('param_'):
                param_id = int(name.replace("param_",""))
                selected_values[param_id] = value
        return selected_values