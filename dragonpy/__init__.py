"""
    dragonpy
    Emulator for 6809 CPU based system like Dragon 32 / CoCo written in Python...
"""


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


__version__ = '0.9.1'
__author__ = 'Jens Diemer <git@jensdiemer.de>'


machine_dict.register(constants.DRAGON32, (run_Dragon32, Dragon32Cfg), default=True)
machine_dict.register(constants.DRAGON64, (run_Dragon64, Dragon64Cfg))
machine_dict.register(constants.COCO2B, (run_CoCo2b, CoCo2bCfg))
machine_dict.register(constants.SBC09, (run_sbc09, SBC09Cfg))
machine_dict.register(constants.SIMPLE6809, (run_Simple6809, Simple6809Cfg))
machine_dict.register(constants.MULTICOMP6809, (run_Multicomp6809, Multicomp6809Cfg))
machine_dict.register(constants.VECTREX, (run_Vectrex, VectrexCfg))
