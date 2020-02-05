from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ansible_merge_vars',
    version='5.0.0',
    description='An Ansible action plugin to explicitly merge inventory variables',  # noqa
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/leapfrogonline/ansible-merge-vars',
    author='Leapfrog Online',
    author_email='dfuchs@leapfrogonline.com',
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='ansible plugin',  # Optional
    py_modules=["ansible_merge_vars"],
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/leapfrogonline/ansible-merge-vars/issues',
        'Source': 'https://github.com/leapfrogonline/ansible-merge-vars/',
    },
)
