import app.models as models
import itertools

class GovernanceTreeBuilder:

    def __init__(self, *args, **kwargs):
        # default variable values
        self.all_processes = {}
        self.all_process_items = {}
        self.generated_trees = {}
        # Introduced items not needing support
        self.introduced_items = []

        processes = models.Process.objects.select_related().prefetch_related().all()

        for proc in processes:
            self.all_processes[proc.id] = proc
            # Each process will additionaly hold lists with the relevant items'
            # ids
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

    def set_introduced_items(self, item_ids):
        """
        Sets the items which will be considered as introduced.
        NB: Clears the current generated trees information
        """
        self.introduced_items = item_ids
        self.generated_trees = {}
    
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

    def pretty_print_support(self, proc):
        return self.retrieve_support(proc).pretty_print(self.all_processes, self.all_process_items)

    def pretty_print_items_support(self, item_ids):
        return self.retrieve_items_support(item_ids).pretty_print(self.all_processes, self.all_process_items)
    
    def retrieve_items_support(self, item_ids):        
        return self.generate_items_or_tree(item_ids, self.get_items_generators_set(item_ids))

    def retrieve_support(self, proc):
        """
        Retrieves a tree (OrTree) expressing the support for a process
        proc: the process with all relevant information
        """
        # Return the cached tree if already calculated
        if str(proc.id) in self.generated_trees:
            return self.generated_trees[str(proc.id)]

        if len(proc.condition_items_ids) == 0:
            return self.generate_no_support_needed_tree(proc)

        return self.generate_or_tree(proc, self.get_items_generators_set(proc.condition_items_ids), proc.condition_items_ids)

    def generate_introduced_support_tree(self, introduced_item_id):
        """
        Generates a tree expressing that a process expects an item to be introduced
        introduced_item_id: The id of the item which has to be introduced
        """
        tree = OrTree(None)
        tree.introduced_item_id = introduced_item_id

        # Return the cached tree if already calculated
        if tree.get_label() in self.generated_trees:
            return self.generated_trees[tree.get_label()]

        # Caching the tree
        self.generated_trees[tree.get_label()] = tree

        return tree

    def generate_no_support_needed_tree(self, proc):
        """
        Generates a tree expressing that a process does not require support
        """
        tree = OrTree(proc.id)
        tree.no_support_needed = True

        # Return the cached tree if already calculated
        if tree.get_label() in self.generated_trees:
            return self.generated_trees[tree.get_label()]

        # Caching the tree
        self.generated_trees[tree.get_label()] = tree

        return tree

    def generate_or_tree(self, proc, possible_process_support_sets, expected_result_items):
        """
        Generates an OrTree representing the disjuncts in which a process can be derived
        proc: the process itself
        possible_process_support_sets: all combinations of processes which can lead to the process
        expected_result_items: the result items which correspond to the processes in the support set
                            The item at position 1 is result of process in tuple position 1, 
                            item 2 for process in tuple position 2 and so on
        """
        tree = OrTree(proc.id)

        # Generating the branches
        for support_set in possible_process_support_sets:
            if len(support_set) > 1:
                # Each branch is an AndTree representing a conjunction of
                # processes
                branch = self.generate_and_tree(support_set, expected_result_items)
                tree.branches[branch.get_label()] = branch
            else:
                # if the support set is just for one process then it can be
                # directly added as an OrTree
                branch = self.retrieve_support(self.all_processes[support_set[0]])
                tree.branches[branch.get_label()] = branch

        # Caching the tree
        self.generated_trees[tree.get_label()] = tree

        return tree

    def generate_items_or_tree(self, item_ids, possible_process_support_sets):
        """
        Generates an OrTree representing the disjuncts in which a list of items can be derived
        item_ids: the ids of the items
        possible_process_support_sets: all combinations of processes which can lead to the items
        """
        tree = OrTree(None)
        tree.item_ids = item_ids

        # Generating the branches
        for support_set in possible_process_support_sets:
            if len(support_set) > 1:
                # Each branch is an AndTree representing a conjunction of
                # processes
                branch = self.generate_and_tree(support_set, item_ids)
                tree.branches[branch.get_label()] = branch
            else:
                # if the support set is just for one process then it can be
                # directly added as an OrTree
                if support_set[0] is not None:
                    branch = self.retrieve_support(self.all_processes[support_set[0]])
                    tree.branches[branch.get_label()] = branch
                # if there is not a supporting process then expect an introduced item
                else:
                    branch = self.generate_introduced_support_tree(item_ids[0])
                    tree.branches[branch.get_label()] = branch

        # Caching the tree
        self.generated_trees[tree.get_label()] = tree

        return tree

    def generate_and_tree(self, process_set, expected_result_items):
        """
        Generates an AndTree representing a conjundtion of set of processes
        process_set: tuple with the relevant process ids
        expected_result_items: the result items which correspond to the processes in the set
                            The item at position 1 is result of process in tuple position 1, 
                            item 2 for process in tuple position 2 and so on
        """
        tree = AndTree(process_set, expected_result_items)
       
        # Return the cached tree if already calculated
        if tree.get_label() in self.generated_trees:
            return self.generated_trees[tree.get_label()]

        # Generating the branches
        for idx, proc_id in enumerate(process_set):
            # Each branch is an OrTree representing the disjunct conditions for
            # a process
            if proc_id is not None:
                branch = self.retrieve_support(self.all_processes[proc_id])
                tree.branches[branch.get_label()] = branch
            else:
                # If the process id is not set, an introduced item (not a
                # process) is expected
                branch = self.generate_introduced_support_tree(expected_result_items[idx])
                tree.branches[branch.get_label()] = branch

        # Caching the tree
        self.generated_trees[tree.get_label()] = tree

        return tree

    def get_items_generators_set(self, item_ids):
        condition_items_generators = [(id, self.get_item_generators(id)) for id in item_ids]

        # Will hold a list of tuples.  Each tuple represents combination of
        # possible processes which lead to this one
        possible_process_support_sets = []
        # Calculating the Cartesian product of the items support to get the
        # process support
        for process_support in itertools.product(*[s[1] for s in condition_items_generators]):
            possible_process_support_sets.append(process_support)

        return possible_process_support_sets

    def get_item_generators(self, item_id):
        """
        Returns the ids of the processes which has the selected item as a result
        If no processes match this criteria returns a list with a None entry
        """
        proc_item_generators = self.all_process_items[item_id].result_in_processes_ids
        if len(proc_item_generators) == 0:
            return [None]
        return proc_item_generators


class AndTree:
        
    def __init__(self, process_ids, expected_result_items):
        # The branches are a dictionary of OrTrees
        self.branches = {}
        # The ids of the processes for which is the tree (tuple)
        self.process_ids = process_ids
        # The items which are needed as results of the processes
        self.expected_result_items = expected_result_items

    def __str__(self, **kwargs):
        return "'{}': {{{}}}".format(self.get_label(), ' AND '.join(str(br) for key, br in self.branches.items()))

    def pretty_print(self, all_processes, all_items, level = 0):
        return '\t' * level +("'{}': {{\n{}\n"+'\t' * level+"}}") \
            .format(self.get_full_label(all_processes, all_items), ("\n"+'\t' * (level+1)+"AND\n") \
                    .join(br.pretty_print(all_processes, all_items,level+1) for key, br in self.branches.items()))

    def get_label(self):
        """ 
        Gets the string label of the tree
        """
        ids = []
        for idx, val in enumerate(self.process_ids):
            if val is not None:
                ids.append(val)
            else:
                # Expecting introduced item
                ids.append("Intr_" + str(self.expected_result_items[idx]))

        return ', '.join(str(x) for x in ids)

    def get_full_label(self, all_processes, all_items):
        """ 
        Gets the label of the tree using the actual process/item
        """
        ids = []
        for idx, val in enumerate(self.process_ids):
            if val is not None:
                ids.append(get_process_name(val, all_processes))
            else:
                # Expecting introduced item
                ids.append("Introducible Item ({})".format(get_item_name(self.expected_result_items[idx], all_items)))

        return ', '.join(str(x) for x in ids)

class OrTree:
        
    def __init__(self, process_id):
        # The id of the process for which is the tree.  Might be None if
        # introduced_item_id or item_ids is set
        self.process_id = process_id
        # The ids of the items for which is the tree
        self.item_ids = None
        # The branches are a dictionary of AndTrees
        self.branches = {}
        # The id of the item which has to be introduced
        self.introduced_item_id = None
        # Id set to True it is assumed that the process does not require any
        # support
        self.no_support_needed = False

    def __str__(self, **kwargs):
        details_info = ""
        if self.introduced_item_id is not None:
            details_info = "Expecting_Introducible_" + str(self.introduced_item_id)
        elif self.no_support_needed:
            details_info = "No_Support_Needed"
        else:
            details_info = "({})".format(' OR '.join(str(br) for key,br in self.branches.items()))

        return "'{}': {}".format(self.get_label(),details_info)

    def pretty_print(self, all_processes, all_items, level = 0):
        details_info = ""
        if self.introduced_item_id is not None:
            details_info = "**Expecting Introducible ({})".format( get_item_name(self.introduced_item_id, all_items))
        elif self.no_support_needed:
            details_info = "**No Prerequisites**"
        else:
            details_info = ("{{\n{}\n"+'\t' * level+"}}") \
                .format(("\n"+'\t' * (level+1)+"OR\n") \
                        .join(br.pretty_print(all_processes, all_items,level+1) for key,br in self.branches.items()))

        return '\t' * level+ "'{}': {}".format(self.get_full_label(all_processes, all_items),details_info)
        
    def get_label(self):
        """ 
        Gets the string label of the tree
        """
        if self.process_id is not None:
            return str(self.process_id)
        if self.item_ids is not None:
            return "Items_"+",".join([str(x) for x in self.item_ids])
        else:
            return "Intr_" + str(self.introduced_item_id)

    def get_full_label(self, all_processes, all_items):
        if self.process_id is not None:
            return get_process_name(self.process_id, all_processes)
        if self.item_ids is not None:
            return "**Items ({})".format(",".join([get_item_name(x, all_items) for x in self.item_ids]))
        else:
            return "**Introducible Item ({})".format(get_item_name(self.introduced_item_id, all_items)) 

def get_process_name(proc_id, all_processes):
    return all_processes[proc_id].name

def get_item_name(item_id, all_items):
    return all_items[item_id].name;