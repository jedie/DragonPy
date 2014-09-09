#!/usr/bin/env python2
# coding: utf-8

"""
    base commandline interface
    ==========================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import argparse
import logging
import os
import sys
from dragonlib.utils.logging_utils import log, setup_logging


def get_log_levels():
    levels = [1] # FIXME
    try:
        # Python 3
        levels += logging._nameToLevel.values()
    except AttributeError:
        # Python 2
        levels += [level for level in logging._levelNames if isinstance(level, int)]


    return levels

LOG_LEVELS = get_log_levels()


class Base_CLI(object):
    DESCRIPTION = None
    EPOLOG = None
    VERSION = None
#     DEFAULT_LOG_FORMATTER = "%(message)s"
    DEFAULT_LOG_FORMATTER = "%(processName)s/%(threadName)s %(message)s"

    def __init__(self):
        self.logfilename = None

        arg_kwargs = {}
        if self.DESCRIPTION is not None:
            arg_kwargs["description"] = self.DESCRIPTION
        if self.EPOLOG is not None:
            arg_kwargs["epilog"] = self.EPOLOG
        if self.VERSION is not None:
            arg_kwargs["version"] = self.VERSION

        self.parser = argparse.ArgumentParser(**arg_kwargs)

        self.parser.add_argument(
            "--verbosity", type=int, choices=LOG_LEVELS, default=logging.CRITICAL,
            help=(
                "verbosity level to stdout (lower == more output!)"
                " (default: %s)" % logging.INFO
            )
        )
        self.parser.add_argument(
            "--log_formatter", default=self.DEFAULT_LOG_FORMATTER,
            help=(
                "see: http://docs.python.org/2/library/logging.html#logrecord-attributes"
            )
        )

    def parse_args(self):
        if self.DESCRIPTION is not None:
            print()
            print(self.DESCRIPTION, self.VERSION)
            print("-"*79)
            print()

        args = self.parser.parse_args()

#         for arg, value in sorted(vars(args).items()):
#             log.debug("argument %s: %r", arg, value)
#             print "argument %s: %r" % (arg, value)

        return args

    def setup_logging(self, args):
        setup_logging(log,
            level=args.verbosity,
            handler=None,
            log_formatter=args.log_formatter
        )


if __name__ == "__main__":
    import doctest
    print(doctest.testmod(
        verbose=False
        # verbose=True
    ))
