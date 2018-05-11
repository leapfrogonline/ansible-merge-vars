from distutils.core import setup


setup(
    name='AnsibleMergeVars',
    description='An Ansible action plugin to explicitly merge inventory variables',
    author='Leapfrog Online',
    author_email='dfuchs@leapfrogonline.com',
    url='https://github.com/leapfrogonline/ansible-merge-vars',
    modules=['merge_vars'],
    version='2.1.0',
)
