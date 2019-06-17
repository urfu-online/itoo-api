#!/usr/bin/env python

from setuptools import setup, find_packages

import itoo_api

setup(
    name='itoo-api',
    version=itoo_api.__version__,
    description='ITOO custom API module for Open edX',
    long_description=open('README.rst').read(),
    author='ITOO',
    url='https://github.com/MasterGowen/itoo-api',
    license='AGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'django>=1.8,<1.9',
        'Pillow',
    ],
)
