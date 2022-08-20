#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# vim:ts=4 sts=4 tw=100:
# pylint: disable-msg=C0103
# pylint: disable-msg=C0301
# pylint: disable-msg=W0611
# pylint: disable-msg=W0612
# pylint: disable-msg=W0702
# pylint: disable-msg=W0703
# pylint: disable-msg=W0621
# pylint: disable-msg=R0913

import re
import os

from setuptools import find_packages, setup

__author__ = "Jaime Filson <wick2o@gmail.com>, Borja Ruiz <borja@libcrack.so>"
__email__ = "wick2o@gmail.com, borja@libcrack.so"
__date__ = "Date: Wed Jan 28 16:35:57 CET 2015"


def read(relpath):
    '''
    Return string containing the contents of the file at *relpath* relative to
    this file.
    '''
    cwd = os.path.dirname(__file__)
    abspath = os.path.join(cwd, os.path.normpath(relpath))
    with open(abspath) as f:
        return f.read()

NAME = 'gitrecon'
VERSION = re.search("__version__ = ([^']+)", read('gitrecon.py')).group(1)
DESCRIPTION = 'Massive GitHub repo clonning.'
KEYWORDS = 'git clone recon'
AUTHOR = __author__
AUTHOR_EMAIL = __email__
URL = 'https://www.github.com/libcrack/gitrecon'
LICENSE = read('LICENSE')
PACKAGES = []
PACKAGE_DATA = {}
PACKAGE_DIR = {}
INSTALL_REQUIRES = [
    x.replace(
        '-',
        '_') for x in read('requirements.txt').split('\n') if x != ''
    ]
LONG_DESC = read('README.md') + '\n\n'
PLATFORMS = ['Linux']
PROVIDES = []
CLASSIFIERS = [
    'Development Status :: 3 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: GPL3',
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
#    'package_data': PACKAGE_DATA,
    'provides': PROVIDES,
    'requires': INSTALL_REQUIRES,
    'install_requires': INSTALL_REQUIRES,
    'classifiers': CLASSIFIERS,
}

setup(**PARAMS)

# vim:ts=4 sts=4 tw=79 expandtab:
