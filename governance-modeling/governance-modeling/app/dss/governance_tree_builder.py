import app.models as models
import itertools

class GovernanceTreeBuilder:
    all_processes = {}
    all_process_items = {}
    process_support = {}

    def __init__(self, *args, **kwargs):
        processes = models.ProjectRequirementCondition.objects.select_related().prefetch_related().all()

        for proc in processes:
            all_processes[proc.id] = proc
            # Each process will additionaly hold lists with the relevant items' ids
            proc.condition_items_ids = []
            proc.prevent_items_ids = []
            proc.result_items_ids = []

            # populating the process and all process items information
            for item in proc.condition_items.all():
                self.add_in_all_items(item)
                proc.condition_items_ids.append(item.id)
                self.all_process_items[item.id].condition_in_processes_ids.append(proc.id)
            for item in proc.prevent_items.all():
                self.add_in_all_items(item)
                proc.prevent_items_ids.append(item.id)
                self.all_process_items[item.id].prevent_in_processes_ids.append(proc.id)
            for item in proc.result_items.all():
                self.add_in_all_items(item)
                proc.result_items_ids.append(item.id)
                self.all_process_items[item.id].result_in_processes_ids.append(proc.id)
    
    def add_in_all_items(self, process_item):
        """
        Adds a process item in the all_process_items dictionary if not already there
        """
        if process_item.id not in self.all_process_items:
            # Creating utility information for relevant processes
            process_item.condition_in_processes_ids = []
            process_item.result_in_processes_ids = []
            process_item.prevent_in_processes_ids = []
            # Adding the item to the all items dict
            self.all_process_items[process_item.id] = process_item

    def retrieve_support(self, proc):
        # Gets list with tuples in format (item_id, [ids of processes in which item is result])
        condition_items_support = \
            [self.retrieve_item_support(item_id) for item_id in proc.condition_items_ids] 
        condition_item_processes = []
    
        condition_items_support = get_items_support( proc.condition_item_ids)

    def retrieve_item_support(self, item_id):
        """
        Returns the ids of the processes which has the selected item as a result
        """
        return (item_id, self.all_process_items[item_id].result_in_processes_ids)

class ProcessSupport:
    process_id = None
    condition_items_support = []
    possible_process_support = []
    is_valid = False

    def __init__(self, process_id, condition_items_support):
        self.process_id = process_id
        self.condition_items_support = condition_items_support
        # generating the carthesian product of the processes which can lead to the 
        # required condition items
        for process_support in itertools.product([s.generating_processes for s in condition_items_support]):
            possible_process_support.append( process_support)
