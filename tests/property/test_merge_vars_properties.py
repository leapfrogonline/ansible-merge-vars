import unittest
from itertools import permutations

from hypothesis import given
from hypothesis import example
import hypothesis.strategies as s

from tests.utils import make_and_run_plugin


def gen_int_lists(num):
    """
    Generate num list strategies of integers

    """
    return [
        s.lists(s.integers(), average_size=10, max_size=100)
        for _ in range(num)
    ]

def gen_dict_lists(num):
    """
    Generate num list strategies of dictionaries

    """
    return [
        s.lists(
            s.dictionaries(
                keys=s.text(),
                values=s.integers(),
                average_size=5,
                max_size=20
            ),
            average_size=10,
            max_size=100
            )
        for _ in range(num)
    ]

def gen_dicts(num):
    """
    Generate num list strategies of integers

    """
    return [
        s.dictionaries(
            keys=s.text(),
            values=s.integers(),
            average_size=10, max_size=100
        )
        for _ in range(num)
    ]


def merge_dicts(dicts):
    """
    Keep updating one dict with the values of the next

    """
    result = {}
    for item in dicts:
        result.update(item)
    return result


class TestMergeVarsProperties(unittest.TestCase):

    @given(*gen_int_lists(3))
    def test_merge_lists(self, list1, list2, list3):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'list',
        }
        task_vars = {
            'var1_whatever__to_merge': list1,
            'var2_whatever__to_merge': list2,
            'var3_whatever__to_merge': list3,
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)

        merged_var = result['ansible_facts']['merged_var']
        possibles = [
            x + y + z
            for x, y, z in permutations([list1, list2, list3])
        ]

        self.assertTrue(
            any([merged_var == x for x in possibles])
        )

    @given(*gen_int_lists(3))
    @example([1, 2, 3], [3, 4, 5], [4, 5, 6])
    def test_dedup_dedups(self, list1, list2, list3):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'dedup': True,
            'expected_type': 'list',
        }
        task_vars = {
            'var1_whatever__to_merge': list1,
            'var2_whatever__to_merge': list2,
            'var3_whatever__to_merge': list3,
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        self.assertTrue(len(merged_var) == len(set(merged_var)))

    @given(*gen_int_lists(3))
    @example([1, 2, 3], [3, 4, 5], [4, 5, 6])
    def test_dedup_includes_all_vals(self, list1, list2, list3):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'dedup': True,
            'expected_type': 'list',
        }
        task_vars = {
            'var1_whatever__to_merge': list1,
            'var2_whatever__to_merge': list2,
            'var3_whatever__to_merge': list3,
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)

        merged_var_set = set(result['ansible_facts']['merged_var'])
        list1_set = set(list1)
        list2_set = set(list2)
        list3_set = set(list2)

        self.assertTrue(list1_set.issubset(merged_var_set))
        self.assertTrue(list2_set.issubset(merged_var_set))
        self.assertTrue(list3_set.issubset(merged_var_set))

    @given(*gen_dicts(3))
    def test_merge_dicts(self, dict1, dict2, dict3):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'dict',
        }
        task_vars = {
            'var1_whatever__to_merge': dict1,
            'var2_whatever__to_merge': dict2,
            'var3_whatever__to_merge': dict3,
        }

        possibles = [
            merge_dicts([x, y, z])
            for x, y, z in permutations([dict1, dict2, dict3])
        ]

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        self.assertTrue(
            any([merged_var == x for x in possibles])
        )
