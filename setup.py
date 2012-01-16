#!/usr/bin/env python

from setuptools import setup

from fandjango import __version__

setup(
    name = 'fandjango',
    version = __version__,
    description = "Fandjango makes it stupidly easy to create Facebook applications with Django.",
    author = "Johannes Gorset",
    author_email = "jgorset@gmail.com",
    url = "http://github.com/jgorset/fandjango",
    packages = [
        'fandjango',
        'fandjango.migrations',
        'fandjango.templatetags'
    ],
    package_data = {
        'fandjango': [
            'templates/fandjango/*',
            'locale/no_NB/LC_MESSAGES/*'
        ]
    },
    install_requires = [
        'facepy >= 0.6.2, < 0.7',
        'requests >= 0.8, < 0.9'
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
