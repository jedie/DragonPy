#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2015 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function
import os

import sys
import subprocess

import MC6809
import click
import dragonpy

from pkg_resources import get_distribution


def get_module_name(package):
    """
    package must have these attributes:
    e.g.:
        package.DISTRIBUTION_NAME = "DragonPyEmulator"
        package.DIST_GROUP = "console_scripts"
        package.ENTRY_POINT = "DragonPy"

    :return: a string like: "dragonpy.core.cli"
    """
    distribution = get_distribution(package.DISTRIBUTION_NAME)
    entry_info = distribution.get_entry_info(package.DIST_GROUP, package.ENTRY_POINT)
    if not entry_info:
        raise RuntimeError(
            "Can't find entry info for distribution: %r (group: %r, entry point: %r)" % (
                package.DISTRIBUTION_NAME, package.DIST_GROUP, package.ENTRY_POINT
            )
        )
    return entry_info.module_name


def get_subprocess_args(package):
    module_name = get_module_name(package)
    subprocess_args = (sys.executable, "-m", module_name)
    return subprocess_args


def _run(*args, **kwargs):
    """
    Run current executable via subprocess and given args
    """
    verbose = kwargs.pop("verbose", False)
    if verbose:
        click.secho(" ".join([repr(i) for i in args]), bg='blue', fg='white')

    executable = args[0]
    if not os.path.isfile(executable):
        raise RuntimeError("First argument %r is not a existing file!" % executable)
    if not os.access(executable, os.X_OK):
        raise RuntimeError("First argument %r exist, but is not executeable!" % executable)

    return subprocess.Popen(args, **kwargs)


def run_dragonpy(*args, **kwargs):
    args = get_subprocess_args(dragonpy) + args
    return _run(*args, **kwargs)


def run_mc6809(*args, **kwargs):
    args = get_subprocess_args(MC6809) + args
    return _run(*args, **kwargs)


if __name__ == '__main__':
    def example(package):
        print(package.__name__)
        module_name = get_module_name(package)
        print("\t* module name:", module_name)
        subprocess_args = get_subprocess_args(package)
        print("\t* subprocess args:", subprocess_args)
        print()

    for package in (dragonpy, MC6809):
        example(package)

    run_dragonpy("--version").wait()
    run_mc6809("--version").wait()