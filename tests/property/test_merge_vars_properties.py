import unittest

from hypothesis import given
from hypothesis import example
import hypothesis.strategies as s

from tests.utils import make_and_run_plugin


def gen_int_lists(num):
    """
    Generate num list strategies of integers

    """
    return [
        s.lists(s.integers(), max_size=100)
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
                max_size=20
            ),
            max_size=100
            )
        for _ in range(num)
    ]


def gen_list_dicts(num):
    """
    Generate num dict strategies of lists

    """
    return [
        s.dictionaries(
            keys=s.text(min_size=1),
            values=s.lists(s.integers(),
                           max_size=100
                          ),
            max_size=20
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
            max_size=100
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
    def test_merge_lists_no_dedup(self, list1, list2, list3):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'dedup': False,
            'expected_type': 'list',
        }
        task_vars = {
            'var1_whatever__to_merge': list1,
            'var2_whatever__to_merge': list2,
            'var3_whatever__to_merge': list3,
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)

        merged_var = result['ansible_facts']['merged_var']
        self.assertEqual(
            merged_var, list1 + list2 + list3
        )

    @given(*gen_int_lists(3))
    @example([1, 2, 3], [3, 4, 5], [4, 5, 6])
    def test_dedup_dedups(self, list1, list2, list3):
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
        self.assertTrue(len(merged_var) == len(set(merged_var)))

    @given(*gen_int_lists(3))
    @example([1, 2, 3], [3, 4, 5], [4, 5, 6])
    def test_dedup_includes_all_vals(self, list1, list2, list3):
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

        merged_var_set = set(result['ansible_facts']['merged_var'])
        list_set = set(list1 + list2 + list3)

        self.assertEqual(merged_var_set, list_set)

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

        expected = merge_dicts([dict1, dict2, dict3])
        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        self.assertEqual(merged_var, expected)

    @given(*gen_list_dicts(3))
    @example({'entry1': [1, 2, 3]}, {'entry1:': [3, 4, 5]}, {'entry2': [4, 5, 6]})
    def test_merge_rec_with_list_dicts(self, dict1, dict2, dict3):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'dict',
            'recursive_dict_merge': True,
        }
        task_vars = {
            'var1_whatever__to_merge': dict1,
            'var2_whatever__to_merge': dict2,
            'var3_whatever__to_merge': dict3,
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']

        # check all keys are present
        self.assertTrue(
            all([
                k in merged_var.keys()
                for k in list(dict1.keys()) + list(dict2.keys()) + list(dict3.keys())
            ])
        )

        # check all list values are present from all input dicts
        self.assertTrue(
            all(
                [set(dict1[k]).issubset(set(merged_var[k])) for k in dict1.keys()] +
                [set(dict2[k]).issubset(set(merged_var[k])) for k in dict2.keys()] +
                [set(dict3[k]).issubset(set(merged_var[k])) for k in dict3.keys()]
            )
        )
