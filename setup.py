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
        'django>=1.11,<2.0',
        'django-model-utils>=1.4.0',
        'djangorestframework>=3.2.0,<3.7.0',
        'djangorestframework-oauth>=1.1.0,<2.0.0',
        'edx-django-oauth2-provider>=1.2.0',
        'edx-drf-extensions>=2.0.0,<3.0.0',
        'edx-opaque-keys>=0.1.2,<1.0.0',
        'Pillow',
    ],
)
