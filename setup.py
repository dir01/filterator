# -*- coding: utf-8 -*-
#!/usr/bin/env python
!/usr/bin/env python

from __future__ import with_statement

import os
from setuptools import setup, find_packages

setup(
    name = 'filterator',
    version = '0.01',
    description = 'Utility for chainable operations upon collections',
    author = 'Andrey Zhu',
    author_email = 'dir01@dir01.org',
    url = 'https://github.com/dir01/filterator',
    packages = find_packages(exclude=['tests', 'tests.*']),
)

