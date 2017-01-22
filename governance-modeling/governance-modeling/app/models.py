"""
Definition of models.
"""

from django.db import models

class ProcessItem(models.Model):
    name = models.CharField(max_length = 255, unique =True)
    description = models.TextField(max_length = 1000, blank=True, null=True,)   
    # condition_in_processes - from Process
    # prevent_in_processes - from Process
    # result_in_processes - from Process
    # condition_in_requirements - from ProjectRequirement
    # prevent_in_requirements - from ProjectRequirement
    # introduced_in_requirements - from ProjectRequirement
    
    def __str__(self):
        return self.name

class Agent(models.Model):
    name = models.CharField(max_length = 255, unique =True)
    # processes - from Process
    
    def __str__(self):
        return self.name

class Process(models.Model):
    name = models.CharField(max_length = 255, unique=True)
    description = models.TextField(max_length = 1000, blank=True, null=True,)   
    agent = models.ForeignKey(Agent, 
                                on_delete=models.PROTECT, 
                                blank=True, 
                                null=True, 
                                related_name="processes")
    condition_items = models.ManyToManyField(ProcessItem, related_name="condition_in_processes")
    prevent_items = models.ManyToManyField(ProcessItem, related_name="prevent_in_processes")
    result_items = models.ManyToManyField(ProcessItem, related_name="result_in_processes")

    def __str__(self):
        return self.name

# The allowed types of a project parameter
PARAMETER_TYPES = (('N', 'Number'),
                    ('S', 'String'),
                    ('B', 'Boolean'),
                    ('E', 'Enum'))

class ProjectParameter(models.Model):
    name = models.CharField(max_length = 255, unique =True)
    description = models.TextField(max_length = 1000, blank=True, null=True,)   
    type = models.CharField(max_length=1, choices = PARAMETER_TYPES)
    # values - from ParameterValue

    def __str__(self):
        return self.name

class ParameterValue(models.Model):
    name = models.CharField(max_length = 255)  
    description = models.TextField(max_length = 1000, blank=True, null=True,)    
    parameter = models.ForeignKey(ProjectParameter, 
                                    on_delete=models.CASCADE,
                                    related_name="values")

    class Meta:
        # Parameters cannot have duplicated values
        unique_together = (("name", "parameter"))

    def __str__(self):
        return self.name

class ProjectRequirement(models.Model):
    name = models.CharField(max_length = 255, unique =True)
    description = models.TextField(max_length = 1000, blank=True, null=True,)   
    condition_items = models.ManyToManyField(ProcessItem, related_name="condition_in_requirements")
    prevent_items = models.ManyToManyField(ProcessItem, related_name="prevent_in_requirements")
    intoruced_items = models.ManyToManyField(ProcessItem, related_name="introduced_in_requirements")
    # conditions - from ProjectRequirementCondition

    def __str__(self):
        return self.name

class ProjectRequirementCondition(models.Model):
    name = models.CharField(max_length = 255, unique =True)
    requirement = models.ForeignKey(ProjectRequirement, 
                                    on_delete=models.CASCADE, 
                                    related_name="conditions")
    condition_parameter = models.ForeignKey(ProjectParameter, on_delete=models.PROTECT)
    parameter_value = models.ForeignKey(ParameterValue, 
                                        on_delete=models.PROTECT, 
                                        blank=True, 
                                        null=True,)
    custom_value = models.CharField(max_length = 100, blank=True, null=True,)

    class Meta:
        # Each requirement can have only one condition using specific param
        unique_together = (("requirement", "condition_parameter"))

    def __str__(self):
        return self.name