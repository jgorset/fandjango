#!/usr/bin/env python

from distutils.core import setup

from fandjango import VERSION

setup(
  name = 'fandjango',
  version = VERSION,
  description = "Fandjango makes it easy to create Facebook applications powered by Django",
  author = "Johannes Gorset",
  author_email = "jgorset@gmail.com",
  url = "http://github.com/jgorset/fandjango",
  packages = ['fandjango', 'fandjango.migrations']
)
