#!/usr/bin/env python

from setuptools import setup

import fandjango

setup(
    name = 'fandjango',
    version = fandjango.__version__,
    description = "Fandjango makes it easy to create Facebook applications with Django.",
    author = "Johannes Gorset",
    author_email = "jgorset@gmail.com",
    url = "http://github.com/jgorset/fandjango",
    packages = ['fandjango', 'fandjango.migrations', 'fandjango.templatetags'],
    package_data = {
        'fandjango': ['templates/*']
    },
    install_requires = [
        'facepy>=0.4.2',
        'requests==0.7.6'
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
