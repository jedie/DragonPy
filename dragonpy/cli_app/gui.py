import locale

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import print  # noqa

from basic_editor.editor import run_basic_editor
from dragonpy.cli_app import app
from dragonpy.cli_arg_types import TyroMachineArgType, TyroMaxOpsArgType, TyroTraceArgType
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import gui_mainloop


# use user's preferred locale
# e.g.: for formatting cycles/sec number
locale.setlocale(locale.LC_ALL, '')


@app.command
def gui(verbosity: TyroVerbosityArgType):
    """<<< **start this** - Start the DragonPy tkinter starter GUI"""
    setup_logging(verbosity=verbosity)
    gui_mainloop(confirm_exit=False)


@app.command
def run(
    machine: TyroMachineArgType,
    trace: TyroTraceArgType,
    max_ops: TyroMaxOpsArgType,
    verbosity: int,  # TODO: use TyroVerbosityArgType
):
    """Run a machine emulation"""
    machine_run_func, MachineConfigClass = machine_dict[machine]
    print(f'Use machine func: {machine_run_func.__name__}')
    cfg_dict = {
        'verbosity': verbosity,  # TODO: Remove and use only logging
        'trace': trace,
        'max_ops': max_ops,
    }
    print(cfg_dict)
    machine_run_func(cfg_dict)


@app.command
def editor(machine: TyroMachineArgType, verbosity: TyroVerbosityArgType):
    """
    Run only the BASIC editor
    """
    setup_logging(verbosity=verbosity)
    machine_run_func, MachineConfigClass = machine_dict[machine]
    cfg_dict = {
        'verbosity': int(verbosity),
        'trace': False,
        'max_ops': None,
    }
    machine_cfg = MachineConfigClass(cfg_dict)
    run_basic_editor(machine_cfg)
