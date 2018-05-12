#!/usr/bin/env python

"""
* Queries PyPI for Ansible versions > 2.0
* Adds all Ansible versions appropriate for each Python version to the tox.ini
* Does not add Ansible versions that are known not to work
"""

from distutils.version import LooseVersion
import os
import re
from string import Template

import requests


ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
TOX_TMPL = os.path.join(ROOT_DIR, 'tox.ini.tmpl')
TOX_INI = os.path.join(ROOT_DIR, 'tox.ini')
INCOMPATIBLE_FILE = os.path.join(ROOT_DIR, 'incompatible_ansible_releases.txt')


def finished(release):
    return not re.search(r'[a-zA-z]', release)


def filter_releases(releases, min_release, incompatible_releases):
    relevant_releases = [
        release for release in releases
        if LooseVersion(release) >= LooseVersion(min_release)
            and finished(release)  # noqa
            and release not in incompatible_releases  # noqa
    ]
    return sorted(relevant_releases, key=LooseVersion)


def tox_dep_specs(releases):
    spec_strings = [
        f'  ansible-{release}: ansible=={release}'
        for release in releases
    ]
    return '\n'.join(spec_strings)


def main():
    # Get incompatible Ansible versions from file
    with open(INCOMPATIBLE_FILE) as f:
        incompatible_releases = [
            release.strip() for release in f.readlines()
        ]

    # Get available releases
    response = requests.get('https://pypi.python.org/pypi/ansible/json').json()
    releases = response['releases'].keys()

    py2_releases = filter_releases(releases, '2.1', incompatible_releases)
    py3_releases = filter_releases(releases, '2.5', incompatible_releases)

    print(f'Reading template {TOX_TMPL}')
    with open(TOX_TMPL, 'r') as f:
        tmpl = Template(f.read())

    generated = tmpl.substitute(
        py2_releases=','.join(py2_releases),
        py3_releases=','.join(py3_releases),
        ansible_dep_specs=tox_dep_specs(py2_releases)
    )
    print(f'\nWriting {TOX_INI}:\n{generated}')

    with open(TOX_INI, 'w') as f:
        f.write(generated)

    print(f'{TOX_INI} written')


if __name__ == "__main__":
    main()
