#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Some needed parts from six:

    https://bitbucket.org/gutworth/six/src/tip/six.py?at=default

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import string
import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if PY3:
    string_types = str,
else:
    string_types = basestring,
    string.ascii_letters = string.letters


if PY3:
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
else:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    exec_("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")


if __name__ == '__main__':
    try:
        raise RuntimeError("Foo Bar")
    except RuntimeError as err:
        msg = "%s | Reraise from six example!" % err
        reraise(RuntimeError, RuntimeError(msg), sys.exc_info()[2])