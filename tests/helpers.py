"""Utility methods for tests."""

import re

def assert_contains(expected, actual):
  if not re.search(expected, actual):
    raise AssertionError("%s does not contain %s" % (actual, expected))
