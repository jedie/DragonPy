#!/usr/bin/env python
# coding: utf-8

"""
    DragonPy - CLI
    ~~~~~~~~~~~~~~

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import sys

if __name__ == "__main__":
    if not hasattr(sys, 'real_prefix'):
        print()
        print("="*79)
        print("ERROR: virtual environment is not activated ?!?")
        print("\ne.g.:")
        print("\t~ $ cd ~/DragonPy_env/")
        print("\t~/DragonPy_env $ source bin/activate")
        print("\t~/DragonPy_env $ cd src/dragonpy")
        print("\t~/DragonPy_env/src/dragonpy $ %s" % " ".join(sys.argv))
        print("-"*79)
        print()

    from dragonpy.core.cli import main
    main()
