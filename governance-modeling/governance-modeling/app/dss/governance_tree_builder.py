import app.models as models

class GovernanceTreeBuilder:
    all_processes = {}
    all_process_items = {}

    def __init__(self, *args, **kwargs):
        processes = models.ProjectRequirementCondition.objects.select_related().prefetch_related().all()

        for proc in processes:
            all_processes[proc.id] = proc
            # Each process will additionaly hold lists with the relevant items' ids
            proc.condition_items_ids = []
            proc.prevent_items_ids = []
            proc.result_items_ids = []

            # populating the process and all process items information
            for item in req.condition_items.all():
                self.add_in_all_items(item)
                proc.condition_items_ids.append(item.id)
            for item in req.prevent_items.all():
                self.add_in_all_items(item)
                proc.condition_items_ids.append(item.id)
            for item in req.introduced_items.all():
                self.add_in_all_items(item)
                proc.condition_items_ids.append(item.id)
    
    def add_in_all_items(self, process_item):
        """
        Adds a process item in the all_process_items dictionary if not already there
        """
        if process_item.id not in self.all_process_items:
            self.all_process_items[process_item.id] = process_item

    def retrieve_support(proc):
        condition_items_support = get_items_support( proc.condition_item_ids)

    def retrieve_item_support(item):
        supporting_processes = get_supporting_process(item)

class Tree:
    or_trees = []
    nodes = []