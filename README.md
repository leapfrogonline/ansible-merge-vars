# ansible_merge_vars: An action plugin for Ansible

[![Travis](https://img.shields.io/travis/leapfrogonline/ansible-merge-vars.svg)](https://travis-ci.org/leapfrogonline/ansible-merge-vars)
[![PyPI](https://img.shields.io/pypi/v/ansible_merge_vars.svg)](https://pypi.org/project/ansible_merge_vars/)

An Ansible plugin to merge all variables in context with a certain suffix (lists
or dicts only) and create a new variable that contains the result of this merge.
This is an Ansible action plugin, which is basically an Ansible module that runs
on the machine running Ansible rather than on the host that Ansible is
provisioning.

- [Installation](#installation)
- [Usage](#usage)
  - [Merging dicts](#merging-dicts)
  - [Merging lists](#merging-lists)
- [Verbosity](#verbosity)
- [Example Playbooks](#example-playbooks)
- [Contributing](#contributing)

## Requirements

This plugin requires Ansible release >= 2.1.0.0.

Additionally, there are some releases of Ansible for which this plugin does not work because of bugs in those releases:
  * [Incompatible Ansible Releases](incompatible_ansible_releases.txt)

## Installation

1. Pick a name that you want to use to call this plugin in Ansible playbooks.
   This documentation assumes you're using the name `merge_vars`.
1. `pip install ansible_merge_vars`
1. Create an `action_plugins` directory in the directory in which you run Ansible.

   By default, Ansible will look for action plugins in an `action_plugins`
   folder adjacent to the running playbook. For more information on this, or to
   change the location where ansible looks for action plugins, see [the Ansible
   docs](https://docs.ansible.com/ansible/dev_guide/developing_plugins.html#distributing-plugins).
1. Create a file called `merge_vars.py` (or whatever name you picked) in the
   `action_plugins` directory, with one line:

   ```
   from ansible_merge_vars import ActionModule
   ```
1. For Ansible less than 2.4:

   1. Create the `library` directory if it's not created yet:
 
      ```
      mkdir -p library
      ```

   1. Create an empty `merge_vars` (or whatever name you picked) file in your `library` directory:

       ```
       touch library/merge_vars
       ```

  Ansible action plugins are usually paired with modules (which run on the
  hosts being provisioned), and Ansible will automatically run an action plugin
  when you call of a module of the same name in a task.  Prior to Ansible 2.4,
  if you want to call an action plugin by its name (`merge_vars`) in our tasks,
  you need an empty file called `merge_vars` in the place where ansible checks
  for custom modules; by default, this is a `library` directory adjacent to the
  running playbook.


## Usage

The variables that you want to merge must be suffixed with `__to_merge`.
They can be defined anywhere in the inventory, or by any other means; as long
as they're in the context for the running play, they'll be merged.

### Merging dicts

Let's say we've got a group `someenvironment` in `group_vars` with a file
`users.yml`, with these contents:

```yaml
users__someenvironment_users__to_merge:
  user1: bob
  user2: henry
```

and a group `somedatacenter` in `groups_vars` with a file `users.yml`, with these
contents:

```yaml
users__somedatacenter_users__to_merge:
  user3: sally
  user4: jane
```

and we're running a play against hosts that are in both of those groups.
Then this task:

```yaml
name: Merge user vars
merge_vars:
  suffix_to_merge: users__to_merge
  merged_var_name: merged_users
  expected_type: 'dict'
```
will set a `merged_users` var (fact) available to all subsequent tasks that looks like this (if it were to be declared in raw yaml):

```yaml
merged_users:
  user1: bob
  user2: henry
  user3: sally
  user4: jane
```

Note that the order in which the dicts get merged is non-deterministic. So this setup:

```yaml
users__someenvironment_users__to_merge:
  user1: bob
  user2: jekyll
```

```yaml
users__somedatacenter_users__to_merge:
  user2: hyde
  user3: sally
```

```yaml
name: Merge user vars
merge_vars:
  suffix_to_merge: users__to_merge
  merged_var_name: merged_users
  expected_type: 'dict'
```

could set a `merged_users` var that looks like this (if it were to be declared in raw yaml:

```yaml
merged_users:
  user1: bob
  user2: jekyll
  user3: sally
```

*OR* this:

```yaml
merged_users:
  user1: bob
  user2: hyde
  user3: sally
```

With great power comes great responsibility...

### Merging lists

Let's say we've got a `someenvironment` group with an `open_ports.yml` file
that looks like this:

```yaml
open_ports__someenvironment_open_ports__to_merge:
  - 1
  - 2
  - 3
```
and a `somedatacenter` group with an `open_ports.yml` file that looks like this:

```yaml
open_ports__somedatacenter_open_ports__to_merge:
  - 3
  - 4
  - 5
```
Then this task:

```yaml
name: Merge open ports
merge_vars:
  suffix_to_merge: open_ports__to_merge
  merged_var_name: merged_ports
  expected_type: 'list'
```
will set a `merged_ports` fact that looks like this:

```yaml
merged_ports:
  - 1
  - 2
  - 3
  - 4
  - 5
```

*OR* this; remember, the order in which variables get merged is non-deterministic:

```yaml
merged_ports:
  - 3
  - 4
  - 5
  - 1
  - 2
```

Notice that `3` only appears once in the merged result. By default, this
`merge_vars` plugin will de-dupe the resulting merged value. If you don't want
to de-dupe the merged value, you have to declare the `dedup` argument:

```yaml
name: Merge open ports
merge_vars:
  suffix_to_merge: open_ports__to_merge
  merged_var_name: merged_ports
  dedup: false
  expected_type: 'list'
```
which will set this fact (or some permutation thereof):

```yaml
merged_ports:
  - 1
  - 2
  - 3
  - 3
  - 4
  - 5
```

A note about `dedup`:
  * It has no effect when the merged vars are dictionaries.

### Recursive merging ###

When dealing with complex data structures, you may want to do a deep (recursive) merge.

Suppose you have variables that define lists of users to add and select who should have admin privileges:

```yaml
users__someenvironment_users__to_merge:
  users:
    - bob
    - henry
  admins:
    - bob
```

and

```yaml
users__somedatacenter_users__to_merge:
  users:
    - sally
    - jane
  admins:
    - sally
```

You can request a recursive merge with:

```yaml
name: Merge user vars
merge_vars:
  suffix_to_merge: users__to_merge
  merged_var_name: merged_users
  expected_type: 'dict'
  recursive_dict_merge: True
```

and get:

```yaml
merged_users:
  users:
    - bob
    - henry
    - sally
    - jane
  admins:
    - bob
    - sally
```

When merging dictionaries and the same key exists in both, the recursive merge checks the type of the value:
* if the entry value is a list, it merges the values as lists (merge_list)
* if the entry value is a dict, it merges the values (recursively) as dicts (merge_dict)
* any other values: just replace (use last)

### Module options ###

| parameter | required | default | choices | comments |
| --------- | -------- | ------- | ------- | -------- |
| suffix_to_merge | yes |        |         | Suffix of variables to merge.  Must end with `__to_merge`. |
| merged_var_name | yes |        | <identifier> | Name of the target variable. |
| expected_type | yes |          | dict, list | Expected type of the merged variable (one of dict or list) |
| dedup     | no       | yes     | yes / no | Whether to remove duplicates from lists (arrays) after merging. |
| cacheable | no       | no      | yes / no | If set to `yes`, the merged variable will be stored in the facts cache |
| recursive_dict_merge | no | no | yes / no | Whether to do deep (recursive) merging of dictionaries, or just merge only at top level and replace values |

## Verbosity

Running ansible-playbook with `-v` will cause this plugin to output the order in
which the keys are being merged:

```
PLAY [Example of merging lists] ************************************************

TASK [Merge port vars] *********************************************************
Merging vars in this order: [u'group2_ports__to_merge', u'group3_ports__to_merge', u'group1_ports__to_merge']
ok: [localhost] => {"ansible_facts": {"merged_ports": [22, 1111, 443, 2222, 80]}, "changed": false}

TASK [debug] *******************************************************************
ok: [localhost] => {
    "merged_ports": [
        22,
        1111,
        443,
        2222,
        80
    ]
}

PLAY RECAP *********************************************************************
localhost                  : ok=6    changed=0    unreachable=0    failed=0
```

## Example Playbooks

There are some example playbooks in the [examples folder](examples) in this
repository. Prerequisites:

  1. You have python 2.7 installed and a `python2.7` executable is on your path.
  1. You have the virtualenv tool installed and a `virtualenv` executable on
     your path.
 
To run all of the example playbooks (from the root of this repository):

    make examples

This will create a virtualenv, install the relevant dependencies into it, and
run each example playbook using the `ansible-playbook` executable in the
virtualenv.

To run a single example, assuming you have your virtualenv and dependencies that
the above make command generates:

    env/bin/ansible-playbook examples/merge_lists_playbook.yml

## Contributing

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

These are the only prerequisites to working on this project locally:

  1. You have [Pipenv](https://docs.pipenv.org) installed.
  1. You have the Python versions in the [.python-version](.python-version)
     installed and on your path (probably with
     [pyenv](https://github.com/pyenv/pyenv)

A development workflow may look like this:

  1. Clone this repository
  1. Run `make deps`
     * This will use [Pipenv](https://docs.pipenv.org) to install all of the
       dependencies needed to build a release and run tests.
  1. Run `make test-all`
     * This will use [tox](https://tox.readthedocs.io/en/latest/) to run the
       tests against different combinations of python versions and ansible
       releases.
     * It will also use [a script](bin/generate_tox_config.py) to query
       [PyPI](https://pypi.python.org) for the latest versions of Ansible, and
       add them to the `tox.ini` file if they're not there.

  1. Updating the `tox.ini` file and running all the tests against all of the
     combinations of Ansible releases and Python versions takes a lot of time.
     To run aginst just one combination, you can list all of the combinations
     available and tell tox to only run the tests for one combination:

     ```
    $ pipenv run tox -l

    py27-ansible-2.1.0.0
    py27-ansible-2.1.1.0
    py27-ansible-2.1.2.0
    py27-ansible-2.1.3.0
    py27-ansible-2.2.0.0
    py27-ansible-2.2.1.0
    ...
    py35-ansible-2.5.1
    py35-ansible-2.5.2
    py36-ansible-2.5.0
    py36-ansible-2.5.1
    py36-ansible-2.5.2
    ...

    $ pipenv run tox -e py36-ansible-2.5.2
    ...
    ```

If you have any ideas about things to add or improve, or find any bugs to fix, we're all ears!  Just a few guidelines:

  1. Please write or update tests (either example-based tests, property-based
     tests, or both) for any code that you add, change, or remove.

  1. Please make sure that `make test-all` exits zero. This runs a code linter,
     all of the tests, and all of the examples against all supported versions
     of Python and Ansible.

  1. If the linting seems too annoying, it probably is! Feel free to do what you
     need to do in the `.pylintrc` at the root of this repository to maintain
     sanity. Add it to your PR, and we'll most likely take it.

Happy merging!
