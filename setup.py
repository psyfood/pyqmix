# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 14:42:48 2017

@author: alfine-l
"""

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    raise sys.exit('Could not import setuptools.')

# Ger version info.
# This basically imports __version__ from version.py.
exec(open('qmix/version.py').read())

setup(
    name='qmix',
    version=__version__,
    author='Lorenzo Alfine <lorenzo.alfine@gmail.com>, Richard Höchenberger <richard.hoechenberger@gmail.com>',
    url='https://github.com/psyfood/Gustometer',
    packages=find_packages(),
    license='GPL v3',
    description='TODO',
    long_description=open('README.md').read(),
    install_requires=['cffi'],
    classifiers=['Intended Audience :: Science/Research',
                 'Programming Language :: Python',
                 'Operating System :: Microsoft :: Windows',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3']
)
