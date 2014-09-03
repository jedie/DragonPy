#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from setuptools import setup, find_packages
import dragonpy

setup(
    name="DragonPy",
    version=dragonpy.__version__,
    py_modules=["DragonPy"],
    provides=["DragonPy"],
    author="Jens Diemer",
    author_email="DragonPy@jensdiemer.de",
    description="Emulator for 6809 CPU based system like Dragon 32 / CoCo written in Python...",
    url="https://github.com/jedie/DragonPy",
    # TODO:
#    entry_points={
#        "console_scripts": ["DragonPy_CLI = mod:func"],
#    },
    license="GPL v3+",
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
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
    test_suite="dragonpy.tests",
)
