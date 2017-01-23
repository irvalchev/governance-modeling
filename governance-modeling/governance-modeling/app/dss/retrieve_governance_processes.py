import app.models as models

def get_active_requirements(param_values):
    """
    Retrieves the requirements which are active based on selected parameter values
    """

    # TODO: this can be optimized
    # These two variables are dictionaries with keys, the requirement and
    # values the conditions
    active_requirements = []
    fulfilled_conditions = {}
    unfulfilled_conditions = {}
    conditions = models.ProjectRequirementCondition.objects.select_related().all()

    # assigning the conditions as fulfilled or unfulfilled
    for condition in conditions:
        if condition.condition_parameter.id in param_values:
            param_value = param_values[condition.condition_parameter.id]
            fulfilled = False
            # checking if the condition is fulfilled
            if condition.condition_parameter.type == models.ProjectParameter.ENUM:
                # when enum compare the id of the selected value
                if int(param_value) in [v.id for v in condition.allowed_values.all()]:
                    fulfilled = True
            else:
                # in all other cases just perform string comparison
                if condition.custom_value == str(param_value):
                    fulfilled = True

            # Assigning the condition to the proper dictionary
            if fulfilled:
                if condition.requirement.id not in fulfilled_conditions:
                    # Creating the list of the fulfilled conditions for the
                    # requirement
                    fulfilled_conditions[condition.requirement.id] = []
                fulfilled_conditions[condition.requirement.id].append(condition)
            else: 
                if condition.requirement.id not in unfulfilled_conditions:
                    # Creating the list of the unfulfilled conditions for the
                    # requirement
                    unfulfilled_conditions[condition.requirement.id] = []
                unfulfilled_conditions[condition.requirement.id].append(condition)
          
    for requirement in fulfilled_conditions:
        # If the requirement is not used as key in
        # unfulfilled_conditions then all its conditions are active
        if requirement not in unfulfilled_conditions:
            active_requirements.append(requirement)
                          
    return active_requirements

def get_requirement_items(req_ids):
    """
    Retrieves a dictionary of process items related to requirements.
    Expects a list of requirement ids as input
    Returns a dictionary with the following keys: 
        introduced_items, condition_items, prevent_items
    """
    req_items = {"introduced_items":[], "condition_items":[], "prevent_items":[]}
    requirements = models.ProjectRequirement.objects.filter(id__in=req_ids).prefetch_related()

    # assigning the conditions as fulfilled or unfulfilled
    for req in requirements:
        for item in req.condition_items.all():
            req_items["condition_items"].append(item)
        for item in req.prevent_items.all():
            req_items["prevent_items"].append(item)
        for item in req.introduced_items.all():
            req_items["introduced_items"].append(item)
                          
    return req_items

def test(req_ids):
    """
    Retrieves a dictionary of process items related to requirements.
    Expects a list of requirement ids as input
    Returns a dictionary with the following keys: 
        introduced_items, condition_items, prevent_items
    """
    req_items = {"introduced_items":[], "condition_items":[], "prevent_items":[]}
    requirements = models.ProjectRequirement.objects.filter(id__in=req_ids).prefetch_related()

    # assigning the conditions as fulfilled or unfulfilled
    for req in requirements:
        for item in req.condition_items.all():
            req_items["condition_items"].append(item)
        for item in req.prevent_items.all():
            req_items["prevent_items"].append(item)
        for item in req.introduced_items.all():
            req_items["introduced_items"].append(item)
                          
    return req_items