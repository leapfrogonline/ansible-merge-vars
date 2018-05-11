#!/usr/bin/env python
from distutils.version import LooseVersion

import requests


def main():
    response = requests.get('https://pypi.python.org/pypi/ansible/json').json()
    releases = response['releases'].keys()
    relevant_releases = [
        release for release in releases
        if LooseVersion(release) >= LooseVersion('2.1')
    ]
    relevant_releases = sorted(relevant_releases, key=LooseVersion)
    import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    main()
