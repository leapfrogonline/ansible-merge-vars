#!/usr/bin/env python

"""
An Ansible action plugin to allow explicit merging of dict and list facts.

"""

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError


# Funky import dance for Ansible backwards compatitility (not sure if we
# actually need to do this or not)
try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display # pylint: disable=ungrouped-imports
    display = Display()


class ActionModule(ActionBase):
    """
    Merge all variables in context with a certain suffix (lists or dicts only)
    and create a new variable that contains the result of this merge. These
    initial suffixed variables can be definied anywhere in the inventory, or by
    any other means; as long as they're in the context for the running play,
    they'll be merged.

    """
    def run(self, tmp=None, task_vars=None):
        suffix_to_merge = self._task.args.get('suffix_to_merge', '')
        merged_var_name = self._task.args.get('merged_var_name', '')
        dedup = self._task.args.get('dedup', True)
        expected_type = self._task.args.get('expected_type')
        all_keys = task_vars.keys()

        # Validate args
        if expected_type not in ['dict', 'list']:
            raise AnsibleError("expected_type must be set ('dict' or 'list').")
        if not suffix_to_merge.endswith('__to_merge'):
            raise AnsibleError("Merge suffix must end with '__to_merge', sorry!")
        if merged_var_name in all_keys:
            warning = "{} is already defined, are you sure you want to overwrite it?"
            display.warning(warning.format(merged_var_name))
            display.v("The contents of {} are: {}".format(
                merged_var_name, task_vars[merged_var_name]))

        keys = [key for key in task_vars.keys()
                if key.endswith(suffix_to_merge)]

        display.v("Merging vars in this order: {}".format(keys))

        merge_vals = [task_vars[key] for key in keys]

        # Dispatch based on type that we're merging
        if merge_vals == []:
            if expected_type == 'list':
                merged = []
            else:
                merged = {} # pylint: disable=redefined-variable-type
        elif isinstance(merge_vals[0], list):
            merged = merge_list(merge_vals, dedup)
        elif isinstance(merge_vals[0], dict):
            merged = merge_dict(merge_vals)
        else:
            raise AnsibleError(
                "Don't know how to merge variables of type: {}".format(type(merge_vals[0]))
            )

        # We need to render any jinja in the merged var now, because once it
        # leaves this plugin, ansible will cleanse it by turning any jinja tags
        # into comments.
        merged = self._templar.template(merged)
        return {
            'ansible_facts': {merged_var_name: merged},
            'changed': False,
        }


def merge_dict(merge_vals):
    """
    To merge dicts, just update one with the values of the next, etc.
    """
    check_type(merge_vals, dict)
    merged = {}
    for val in merge_vals:
        merged.update(val)
    return merged


def merge_list(merge_vals, dedup):
    """ To merge lists, just concat them. Dedup if wanted. """
    check_type(merge_vals, list)
    merged = flatten(merge_vals)
    if dedup:
        merged = deduplicate(merged)
    return merged


def check_type(mylist, _type):
    """ Ensure that all members of mylist are of type _type. """
    if not all([isinstance(item, _type) for item in mylist]):
        raise AnsibleError("All values to merge must be of the same type, either dict or list")


def flatten(list_of_lists):
    """
    Flattens a list of lists:
        >>> flatten([[1, 2] [3, 4]])
        [1, 2, 3, 4]

    I wish Python had this in the standard lib :(
    """
    return list((x for y in list_of_lists for x in y))


def deduplicate(mylist):
    """
    Just brute force it. This lets us keep order, and lets us dedup unhashable
    things, like dicts. Hopefully you won't run into such big lists that
    this will ever be a performance issue.
    """
    deduped = []
    for item in mylist:
        if item not in deduped:
            deduped.append(item)
    return deduped
