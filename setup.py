#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    raise sys.exit('Could not import setuptools.')

# Get version info.
# This basically imports __version__ from version.py.
exec(open('pyqmix/version.py').read())

setup(
    name='pyqmix',
    version=__version__,
    author=('Lorenzo Alfine <lorenzo.alfine@gmail.com>,'
            'Richard Höchenberger <richard.hoechenberger@gmail.com>'),
    url='https://github.com/psyfood/Gustometer',
    packages=find_packages(),
    license='GPL v3',
    description='A wrapper for the Cetoni Qmix SDK.',
    long_description=open('README.md').read(),
    install_requires=['cffi', 'ruamel.yaml', 'appdirs'],
    classifiers=['Intended Audience :: Science/Research',
                 'Programming Language :: Python',
                 'Operating System :: Microsoft :: Windows',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3']
)
