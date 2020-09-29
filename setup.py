#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import itoo_api


def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


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
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'django>2.2',
        'Pillow',
    ],
    package_data=package_data("itoo_api", ["templates"]),
)
