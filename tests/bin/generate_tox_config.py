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


def filter_releases(releases, min_release, max_release=None):
    """
    min_release inclusive, max_release exclusive
    """
    finished = [release for release in releases
                if not re.search(r'[a-zA-z]', release)]
    minor = list(set(
        [re.match(r'^(\d+\.\d+)', release).groups()[0] for release in finished]
    ))

    relevant = minor
    if min_release:
        relevant = [
            release for release in relevant
            if LooseVersion(release) >= LooseVersion(min_release)
        ]

    if max_release:
        relevant = [
            release for release in relevant
            if LooseVersion(release) < LooseVersion(max_release)
        ]
    return sorted(relevant, key=LooseVersion)


def tox_dep_specs(releases):
    spec_strings = [
        '  ansible-{release}: ansible~={release}.0'.format(release=release)
        for release in releases
    ]
    return '\n'.join(spec_strings)


def jinja_dep_specs(releases):
    spec_strings = [
        '  ansible-{release}: jinja2<3.1'.format(release=release)
        for release in releases
    ]
    return '\n'.join(spec_strings)


def main():
    # Get available releases
    response = requests.get('https://pypi.python.org/pypi/ansible/json').json()
    releases = response['releases'].keys()

    all_releases = filter_releases(releases, min_release='2.1')
    py27_releases = filter_releases(releases, min_release='2.1', max_release='5.0')
    py35_releases = filter_releases(releases, min_release='2.5', max_release='5.0')
    py36_releases = filter_releases(releases, min_release='2.5', max_release='5.0')
    py37_releases = filter_releases(releases, min_release='2.5', max_release='5.0')
    py38_releases = filter_releases(releases, min_release='2.8', max_release='7.0')
    py39_releases = filter_releases(releases, min_release='2.8', max_release='9.0')
    py310_releases = filter_releases(releases, min_release='2.8')
    py311_releases = filter_releases(releases, min_release='2.8')

    # https://github.com/ansible/ansible/issues/81946
    py312_releases = filter_releases(releases, min_release='6.0')

    # Some old releases didn't constrain Jinja properly and a newer version breaks some filters
    # https://github.com/ansible/ansible/issues/77356
    old_jinja_releases = filter_releases(releases, min_release=None, max_release='2.10')

    print('Reading template {}'.format(TOX_TMPL))
    with open(TOX_TMPL, 'r') as f:
        tmpl = Template(f.read())

    generated = tmpl.substitute(
        py27_releases=','.join(py27_releases),
        py35_releases=','.join(py35_releases),
        py36_releases=','.join(py36_releases),
        py37_releases=','.join(py37_releases),
        py38_releases=','.join(py38_releases),
        py39_releases=','.join(py39_releases),
        py310_releases=','.join(py310_releases),
        py311_releases=','.join(py311_releases),
        py312_releases=','.join(py312_releases),
        ansible_dep_specs=tox_dep_specs(all_releases),
        jinja_dep_specs=jinja_dep_specs(old_jinja_releases)
    )
    print('\nWriting {TOX_INI}:\n{generated}'.format(TOX_INI=TOX_INI, generated=generated))

    with open(TOX_INI, 'w') as f:
        f.write(generated)

    print('{} written'.format(TOX_INI))


if __name__ == "__main__":
    main()
