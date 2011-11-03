#!/usr/bin/env python

from setuptools import setup

import fandjango

setup(
    name = 'fandjango',
    version = fandjango.__version__,
    description = "Fandjango makes it easy to create Facebook applications powered by Django",
    author = "Johannes Gorset",
    author_email = "jgorset@gmail.com",
    url = "http://github.com/jgorset/fandjango",
    packages = ['fandjango', 'fandjango.migrations', 'fandjango.templatetags'],
    package_data = {
        'fandjango': ['templates/*']
    },
    install_requires = ['facepy>=0.4.2']
)
