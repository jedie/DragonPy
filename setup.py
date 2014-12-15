#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages
import os
import sys

import dragonpy


PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


# convert creole to ReSt on-the-fly, see also:
# https://code.google.com/p/python-creole/wiki/UseInSetup
try:
    from creole.setup_utils import get_long_description
except ImportError as err:
    if "check" in sys.argv or "register" in sys.argv or "sdist" in sys.argv or "--long-description" in sys.argv:
        raise ImportError("%s - Please install python-creole >= v0.8 -  e.g.: pip install python-creole" % err)
    long_description = None
else:
    long_description = get_long_description(PACKAGE_ROOT)


setup(
    name="DragonPyEmulator", # Name conflict with https://github.com/jpanganiban/dragonpy :(
    version=dragonpy.__version__,
    py_modules=["DragonPy"],
    provides=["DragonPy"],
    install_requires=[
        "dragonlib",
        "pygments",
    ],
    author="Jens Diemer",
    author_email="DragonPy@jensdiemer.de",
    description="Emulator for 6809 CPU based system like Dragon 32 / CoCo written in Python...",
    keywords="Emulator 6809 Dragon CoCo Vectrex tkinter pypy",
    long_description=long_description,
    url="https://github.com/jedie/DragonPy",
    # TODO:
#    entry_points={
#        "console_scripts": ["DragonPy_CLI = mod:func"],
#    },
    license="GPL v3+",
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Emulators",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Testing",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="dragonpy.tests", # or: .../dragonpy $ python3 -m unittest discover
)
