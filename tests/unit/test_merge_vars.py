import unittest

from tests.utils import make_and_run_plugin


class TestMergeVars(unittest.TestCase):
    def test_returns_unchanged(self):
        """Execution returns 'unchanged' status in ansible"""
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'list',
        }
        result = make_and_run_plugin(task_args=task_args, task_vars={})
        self.assertFalse(result['changed'])

    def test_list_returns_empty_list(self):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'list',
        }
        expected = {'merged_var': []}
        result = make_and_run_plugin(task_args=task_args, task_vars={})
        self.assertEqual(result['ansible_facts'], expected)

    def test_render_jinja(self):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'list',
        }
        task_vars = {
            'some_var': 'woohoo',
            'some_other_var': 'bar',
            'var1_whatever__to_merge': ['{{ some_var }}'],
            'var2_whatever__to_merge': ['foo{{ some_other_var }}']
        }
        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']

        self.assertEqual(merged_var, [u'woohoo', u'foobar'])

    def test_render_nested_jinja(self):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'list',
        }
        task_vars = {
            'some_var': 'woohoo',
            'some_other_var': 'bar',
            'yet_another_var': '{{ some_var }}-{{ some_other_var }}',
            'var1_whatever__to_merge': ['{{ some_var }}'],
            'var2_whatever__to_merge': [{u'some_key': '{{ yet_another_var }}'}]
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        self.assertEqual(
            merged_var, [u'woohoo', {u'some_key': u'woohoo-bar'}]
        )

        self.assertIn('woohoo', merged_var)
        self.assertIn({'some_key': u'woohoo-bar'}, merged_var)

    def test_render_complex_jinja(self):
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'expected_type': 'dict',
            'recursive_dict_merge': True,
        }
        task_vars = {
            'some_var': '{{ {1: 1, 2: 2} }}',
            'some_other_var': '{{ {3:3} }}',
            'var1_whatever__to_merge': {'foo': '{{ some_var }}'},
            'var2_whatever__to_merge': {'foo': '{{ some_other_var }}'},
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        expected = {'foo': {1: 1, 2: 2, 3: 3}}
        self.assertEqual(expected, merged_var)

    def test_dedupe_preserves_order(self):
        """
        Order of dedup'd lists is preserved. This too is a bit hairy to test
        with properties

        """
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'dedup': True,
            'expected_type': 'list',
        }

        list1 = [1, 2, 3]
        list2 = [3, 4, 5]
        list3 = [5, 6, 7]
        task_vars = {
            'var1_whatever__to_merge': list1,
            'var2_whatever__to_merge': list2,
            'var3_whatever__to_merge': list3,
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        self.assertEqual(merged_var, [1, 2, 3, 4, 5, 6, 7])

    def test_dedup_unhashable(self):
        """
        Lists with unhashable elements get deduped. This is too hairy to test
        with properties, because... it's inneficient to dup-check lists of
        unhashable things :)

        """
        task_args = {
            'suffix_to_merge': 'whatever__to_merge',
            'merged_var_name': 'merged_var',
            'dedup': True,
            'expected_type': 'list',
        }
        task_vars = {
            'var1_whatever__to_merge': [
                {'subvar_a': 1},
                {'subvar_b': 2},
            ],
            'var2_whatever__to_merge': [
                {'subvar_b': 2},
                {'subvar_c': 3},
            ],
        }

        result = make_and_run_plugin(task_args=task_args, task_vars=task_vars)
        merged_var = result['ansible_facts']['merged_var']
        self.assertEqual(
            merged_var, [{'subvar_a': 1}, {'subvar_b': 2}, {'subvar_c': 3}]
        )
