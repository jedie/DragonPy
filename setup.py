#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="DragonPy",
    version="0.1",
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
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: System :: Emulators",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Testing",
    ],
    test_suite="tests",
)
