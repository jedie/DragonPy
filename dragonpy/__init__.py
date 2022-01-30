import os
import sys

from dragonpy import constants
from dragonpy.CoCo.config import CoCo2bCfg
from dragonpy.CoCo.machine import run_CoCo2b
from dragonpy.core.configs import machine_dict
from dragonpy.Dragon32.config import Dragon32Cfg
from dragonpy.Dragon32.machine import run_Dragon32
from dragonpy.Dragon64.config import Dragon64Cfg
from dragonpy.Dragon64.machine import run_Dragon64
from dragonpy.Multicomp6809.config import Multicomp6809Cfg
from dragonpy.Multicomp6809.machine import run_Multicomp6809
from dragonpy.sbc09.config import SBC09Cfg
from dragonpy.sbc09.machine import run_sbc09
from dragonpy.Simple6809.config import Simple6809Cfg
from dragonpy.Simple6809.machine import run_Simple6809
from dragonpy.vectrex.config import VectrexCfg
from dragonpy.vectrex.machine import run_Vectrex


__version__ = "0.7.0"


# Used in setup.py and starter GUI to find the cli-executeable:
DISTRIBUTION_NAME = "DragonPyEmulator"
DIST_GROUP = "console_scripts"
ENTRY_POINT = "DragonPy"

machine_dict.register(constants.DRAGON32, (run_Dragon32, Dragon32Cfg), default=True)
machine_dict.register(constants.DRAGON64, (run_Dragon64, Dragon64Cfg))
machine_dict.register(constants.COCO2B, (run_CoCo2b, CoCo2bCfg))
machine_dict.register(constants.SBC09, (run_sbc09, SBC09Cfg))
machine_dict.register(constants.SIMPLE6809, (run_Simple6809, Simple6809Cfg))
machine_dict.register(constants.MULTICOMP6809, (run_Multicomp6809, Multicomp6809Cfg))
machine_dict.register(constants.VECTREX, (run_Vectrex, VectrexCfg))


def fix_virtualenv_tkinter():
    """
    work-a-round for tkinter under windows in a virtualenv:
      "TclError: Can't find a usable init.tcl..."
    Known bug, see: https://github.com/pypa/virtualenv/issues/93

    There are "fix tk" file here:

          C:\\Python27\\Lib\\lib-tk\\FixTk.py
          C:\\Python34\\Lib\tkinter\\_fix.py

    These modules will be automatic imported by tkinter import.

    The fix set theses environment variables:

        TCL_LIBRARY C:\\Python27\tcl\tcl8.5
        TIX_LIBRARY C:\\Python27\tcl\tix8.4.3
        TK_LIBRARY C:\\Python27\tcl\tk8.5

        TCL_LIBRARY C:\\Python34\tcl\tcl8.6
        TIX_LIBRARY C:\\Python34\tcl\tix8.4.3
        TK_LIBRARY C:\\Python34\tcl\tk8.6

    but only if:

          os.path.exists(os.path.join(sys.prefix,"tcl"))

    And the virtualenv activate script will change the sys.prefix
    to the current env. So we temporary change it back to sys.real_prefix
    and import the fix module.
    If the fix module was imported before, then we reload it.
    """
    if "TCL_LIBRARY" in os.environ:
        # Fix not needed (e.g. virtualenv issues #93 fixed?)
        return

    if not hasattr(sys, "real_prefix"):
        # we are not in a activated virtualenv
        return

    virtualprefix = sys.base_prefix
    sys.base_prefix = sys.real_prefix

    try:
        from tkinter import _fix
    except ImportError as err:
        print(f'Can not apply windows tkinter fix: {err}')
    else:
        if "TCL_LIBRARY" not in os.environ:
            from importlib import reload
            reload(_fix)

    sys.base_prefix = virtualprefix


if sys.platform.startswith("win"):
    fix_virtualenv_tkinter()
