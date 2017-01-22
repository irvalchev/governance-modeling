import app.models as models
from django.contrib import admin
from app.forms import ProjectRequirementConditionForm

@admin.register(models.Process,
                models.ProcessItem,
                models.Agent, 
                models.ProjectRequirement,
                models.ProjectParameter,
                models.ParameterValue)
class AppModelsAdmin(admin.ModelAdmin):
    pass

@admin.register(models.ProjectRequirementCondition)
class ProjectRequirementConditionAdmin(admin.ModelAdmin):
    form = ProjectRequirementConditionForm
    pass