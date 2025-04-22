from typing import Annotated

import tyro

from dragonpy.core.configs import machine_dict


TyroTraceArgType = Annotated[
    bool,
    tyro.conf.arg(
        default=False,
        help='Create trace lines',
    ),
]
TyroMaxOpsArgType = Annotated[
    int,
    tyro.conf.arg(default=None, help='If given: Stop CPU after given cycles else: run forever'),
]

TyroMachineArgType = Annotated[
    str,
    tyro.conf.arg(
        default=machine_dict.DEFAULT,
        help=f'Used machine configuration, one of: {sorted(machine_dict.keys())}',
    ),
]
