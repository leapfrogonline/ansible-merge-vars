#!/usr/bin/env python

"""
* Queries PyPI for Ansible versions > 2.0
* Adds all Ansible versions appropriate for each Python version to the tox.ini
* Does not add Ansible versions that are known not to work

While this plugin still supports Python 2.7, this script needs to be
2.7-compatible, because it will be run in CI using 2.7.
"""

from distutils.version import LooseVersion
import os
import re
from string import Template

import requests


ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
TOX_TMPL = os.path.join(ROOT_DIR, 'tox.ini.tmpl')
TOX_INI = os.path.join(ROOT_DIR, 'tox.ini')


def filter_releases(releases, min_release):
    finished = [release for release in releases
                if not re.search(r'[a-zA-z]', release)]
    minor = list(set(
        [re.match(r'^(\d+\.\d+)', release).groups()[0] for release in finished]
    ))
    relevant = [
        release for release in minor
        if LooseVersion(release) >= LooseVersion(min_release)
    ]
    return sorted(relevant, key=LooseVersion)


def tox_dep_specs(releases):
    spec_strings = [
        '  ansible-{release}: ansible=={release}'.format(release=release)
        for release in releases
    ]
    return '\n'.join(spec_strings)


def main():
    # Get available releases
    response = requests.get('https://pypi.python.org/pypi/ansible/json').json()
    releases = response['releases'].keys()

    py2_releases = filter_releases(releases, '2.1')
    py3_releases = filter_releases(releases, '2.5')
    py38_releases = filter_releases(releases, '2.8')

    print('Reading template {}'.format(TOX_TMPL))
    with open(TOX_TMPL, 'r') as f:
        tmpl = Template(f.read())

    generated = tmpl.substitute(
        py2_releases=','.join(py2_releases),
        py3_releases=','.join(py3_releases),
        py38_releases=','.join(py38_releases),
        ansible_dep_specs=tox_dep_specs(py2_releases)
    )
    print('\nWriting {TOX_INI}:\n{generated}'.format(TOX_INI=TOX_INI, generated=generated))

    with open(TOX_INI, 'w') as f:
        f.write(generated)

    print('{} written'.format(TOX_INI))


if __name__ == "__main__":
    main()
