#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: borja@libcrack.so
# Date: Wed Jan 28 16:35:57 CET 2015

import re
import os

from setuptools import find_packages, setup


def read(relpath):
    cwd = os.path.dirname(__file__)
    abspath = os.path.join(cwd,
                           os.path.normpath(relpath))
    with open(abspath) as f:
        return f.read()

NAME = 'gitrecon'
VERSION = re.search("__version__ = ([^']+)",
                   read('gitrecon.py')).group(1)
DESCRIPTION = 'Massive GIT repo clonning using a GitHub username.'
KEYWORDS = 'git'
AUTHOR = 'libcrack'
AUTHOR_EMAIL = 'devnull@libcrack.so'
URL = 'https://www.github.com/libcrack/gitrecon'
LICENSE = read('LICENSE')
#PACKAGES = find_packages(exclude=['tests', 'tests.*'])
PACKAGES = [NAME]
PACKAGE_DATA = {NAME: ['data/*'],}
PACKAGE_DIR = {NAME: 'src'}
INSTALL_REQUIRES = [
    x.replace(
        '-',
        '_') for x in read('requirements.txt').split('\n') if x != '']
#TEST_SUITE = 'tests'
#TESTS_REQUIRE = ['behave', 'mock', 'pyparsing', 'pytest']
LONG_DESC = read('README.md') + '\n\n' + read('CHANGES')
PLATFORMS = ['Linux']
PROVIDES = [NAME]
CLASSIFIERS = [
    'Development Status :: 3 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: Other/Propietary License',
    'Operating System :: OS Independent',
    'Operating System :: POSIX :: Linux',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

PARAMS = {
    'platforms': PLATFORMS,
    'name': NAME,
    'version': VERSION,
    'description': DESCRIPTION,
    'keywords': KEYWORDS,
    'long_description': LONG_DESC,
    'author': AUTHOR,
    'author_email': AUTHOR_EMAIL,
    'url': URL,
    'license': LICENSE,
    'packages': PACKAGES,
    'package_dir': PACKAGE_DIR,
    'package_data': PACKAGE_DATA,
    'provides': PROVIDES,
    'requires': INSTALL_REQUIRES,
    'install_requires': INSTALL_REQUIRES,
    #'tests_require':    TESTS_REQUIRE,
    #'test_suite':       TEST_SUITE,
    'classifiers': CLASSIFIERS,
}

setup(**PARAMS)

# vim:ts=4 sts=4 tw=79 expandtab:
