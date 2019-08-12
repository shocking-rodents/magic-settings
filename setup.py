# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup


def read(filename: str) -> str:
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()


def get_version() -> str:
    """Get version from the package without actually importing it."""
    init = read('magic_settings/__init__.py')
    for line in init.split('\n'):
        if line.startswith('__version__'):
            return eval(line.split('=')[1])


setup(
    name='magic-settings',
    version=get_version(),
    description='Configuration manager for Python applications.',
    packages=find_packages(exclude=['tests', ]),
    keywords='parser config environment settings configuration',
    url='https://github.com/shocking-rodents/magic-settings/',
    download_url='https://pypi.org/project/magic-settings/',
    author='Anton Ostapenko',
    author_email='olsnod@gmail.com',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    python_requires='~=3.6',
    zip_safe=True,
    install_requires=[
        'python-dotenv~=0.10.2',
    ],
    extras_require={
        'yaml': [
            'PyYAML~=5.1'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],

)
