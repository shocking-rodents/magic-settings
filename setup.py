import os
from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def get_version():
    """Get version from the package without actually importing it."""
    init = read('magic_settings/__init__.py')
    for line in init.split('\n'):
        if line.startswith('__version__'):
            return eval(line.split('=')[1])


setup(name='magic-settings',
      version=get_version(),
      description='magic parser is a library for parsing configs',
      keywords='parser config environment variable',
      url='https://git.angrydev.ru/public_repos/magic-settings/tree/develop',
      author='Angry Developers',
      author_email='guseynov@angrydev.ru',
      license='Apache 2.0',
      packages=['magic_settings'],
      include_package_data=True,
      zip_safe=False)
