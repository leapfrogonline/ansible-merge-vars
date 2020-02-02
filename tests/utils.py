"""
Helpers for example and property-based tests

"""

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
import mock

from ansible_merge_vars import ActionModule as MV


def make_and_run_plugin(task_args, task_vars):
    """
    Build and run an instance of the action plugin configured with the passed
    vars and args

    """
    templar = Templar(loader=DataLoader())
    templar.set_available_variables(task_vars)
    task = mock.MagicMock(args=task_args)
    plugin = MV(
        task=task,
        connection=None,
        play_context=None,
        loader=None,
        templar=templar,
        shared_loader_obj=None,
    )
    return plugin.run(tmp=None, task_vars=task_vars)
