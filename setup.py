#!/usr/bin/env python

import setuptools
from distutils.core import setup

execfile('trapperkeeper/version.py')

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

kwargs = {
    "name": "trapperkeeper",
    "version": str(__version__),
    "packages": ["trapperkeeper"],
    "package_data": {"trapperkeeper": [
        "plugins/loaders/*.py",
        "plugins/hooks/*.py",
        "plugins/executors/*.py",
    ]},
    "scripts": ["bin/trapperkeeper"],
    "description": "Pluggable Distributed SSH Command Executer.",
    # PyPi, despite not parsing markdown, will prefer the README.md to the
    # standard README. Explicitly read it here.
    "long_description": open("README").read(),
    "author": "Gary M. Josack",
    "maintainer": "Gary M. Josack",
    "author_email": "gary@byoteki.com",
    "maintainer_email": "gary@byoteki.com",
    "license": "Apache",
    "install_requires": required,
    "url": "https://github.com/dropbox/trapperkeeper",
    "download_url": "https://github.com/dropbox/trapperkeeper/archive/master.tar.gz",
    "classifiers": [
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}

setup(**kwargs)
