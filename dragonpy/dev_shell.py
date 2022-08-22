import argparse
import locale
import logging
from pathlib import Path
from pprint import pprint

import cmd2
from cmd2 import Cmd2ArgumentParser
from creole.setup_utils import assert_rst_readme
from dev_shell.base_cmd2_app import DevShellBaseApp, run_cmd2_app
from dev_shell.command_sets import DevShellBaseCommandSet
from dev_shell.command_sets.dev_shell_commands import DevShellCommandSet as OriginDevShellCommandSet
from dev_shell.config import DevShellConfig
from dev_shell.utils.colorful import blue, bright_blue, bright_yellow, cyan, print_error
from dev_shell.utils.subprocess_utils import verbose_check_call
from poetry_publish.publish import poetry_publish

import dragonpy
from basic_editor.editor import run_basic_editor
from dragonpy.components.rom import ROMDownloadError
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import VERBOSITY_DICT, gui_mainloop


PACKAGE_ROOT = Path(dragonpy.__file__).parent.parent.parent


# use user's preferred locale
# e.g.: for formating cycles/sec number
locale.setlocale(locale.LC_ALL, '')


def add_argument_machine(parser: Cmd2ArgumentParser):
    parser.add_argument(
        '--machine',
        choices=sorted(machine_dict.keys()),
        default=machine_dict.DEFAULT,
        help='Used machine configuration (default: %(default)s)',
    )


def add_argument_verbosity(parser: Cmd2ArgumentParser):
    parser.add_argument(
        '--verbosity',
        type=int,
        choices=sorted(VERBOSITY_DICT.keys()),
        default=99,
        help='verbosity level to stdout (default: %(default)s)',
    )


@cmd2.with_default_category('DragonPy commands')
class DragonPyCommandSet(DevShellBaseCommandSet):
    def do_gui(self, statement: cmd2.Statement):
        """
        Start the DragonPy tkinter starter GUI
        """
        gui_mainloop(confirm_exit=False)

    def do_download_roms(self, statement: cmd2.Statement):
        """
        Download/Test only ROM files
        """
        roms = list(machine_dict.items())
        print(f'Download {len(roms)} platform roms...')
        success = 0
        for machine_name, data in roms:
            machine_config = data[1]
            print(blue(f'Download / test ROM for {bright_blue(machine_name)}:'))

            for rom in machine_config.DEFAULT_ROMS:
                print(f"\tROM file: {cyan(rom.FILENAME)}")
                try:
                    content = rom.get_data()
                except ROMDownloadError as err:
                    print_error(f'Download {err.url!r} -> {err.origin_err}')
                    continue

                size = len(content)
                print(f"\tfile size is ${size:04x} (dez.: {size:d}) Bytes\n")
                success += 1

        print(f'{success} ROMs succeed.')

    run_parser = cmd2.Cmd2ArgumentParser()
    add_argument_machine(run_parser)
    run_parser.add_argument(
        '--max-ops',
        type=int,
        default=None,
        help='If given: Stop CPU after given cycles else: run forever (default: %(default)s)',
    )
    run_parser.add_argument(
        '--trace',
        action='store_true',
        help='Create trace lines (default: %(default)s)',
    )
    add_argument_verbosity(run_parser)

    @cmd2.with_argparser(run_parser, preserve_quotes=True)
    def do_run(self, ns: argparse.Namespace):
        """
        Run a machine emulation
        """
        machine_run_func, MachineConfigClass = machine_dict[ns.machine]
        print("Use machine func: %s", machine_run_func.__name__)
        cfg_dict = {
            'verbosity': ns.verbosity,
            'trace': ns.trace,
            'max_ops': ns.max_ops,
        }
        pprint(cfg_dict)
        machine_run_func(cfg_dict)

    run_editor = cmd2.Cmd2ArgumentParser()
    add_argument_machine(run_editor)
    add_argument_verbosity(run_editor)

    @cmd2.with_argparser(run_editor, preserve_quotes=True)
    def do_editor(self, ns: argparse.Namespace):
        """
        Run only the BASIC editor
        """
        machine = ns.machine
        machine_run_func, MachineConfigClass = machine_dict[machine]
        cfg_dict = {
            'verbosity': ns.verbosity,
            'trace': False,
            'max_ops': None,
        }
        machine_cfg = MachineConfigClass(cfg_dict)
        run_basic_editor(machine_cfg)

    def do_log_list(self, statement: cmd2.Statement):
        """
        List all exiting loggers and exit.
        """
        print("A list of all loggers:")
        for log_name in sorted(logging.Logger.manager.loggerDict):
            print(f"\t{log_name}")


class DevShellCommandSet(OriginDevShellCommandSet):

    def do_publish(self, statement: cmd2.Statement):
        """
        Publish "dev-shell" to PyPi
        """
        # don't publish if README is not up-to-date:
        assert_rst_readme(package_root=PACKAGE_ROOT, filename='README.creole')

        # don't publish if code style wrong:
        verbose_check_call('darker', '--check')

        # don't publish if test fails:
        verbose_check_call('pytest', '-x')

        poetry_publish(
            package_root=PACKAGE_ROOT,
            version=dragonpy.__version__,
            creole_readme=True,  # don't publish if README.rst is not up-to-date
        )


class DevShellApp(DevShellBaseApp):
    # Remove some commands:
    delattr(cmd2.Cmd, 'do_edit')
    delattr(cmd2.Cmd, 'do_shell')
    delattr(cmd2.Cmd, 'do_run_script')
    delattr(cmd2.Cmd, 'do_run_pyscript')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intro = f'Developer shell - {bright_yellow("DragonPy")} - v{dragonpy.__version__}\n'
        self.intro += """
            ********************************************************
            * DragonPy is a Open source (GPL v3 or later) emulator *
            * for the 30 years old homecomputer Dragon 32          *
            * and Tandy TRS-80 Color Computer (CoCo)...            *
            ********************************************************
            * Homepage: https://github.com/jedie/DragonPy          *
            ********************************************************
        """


def get_devshell_app_kwargs():
    """
    Generate the kwargs for the cmd2 App.
    (Separated because we needs the same kwargs in tests)
    """
    config = DevShellConfig(package_module=dragonpy)

    # initialize all CommandSet() with context:
    kwargs = dict(config=config)

    app_kwargs = dict(
        config=config,
        command_sets=[
            DragonPyCommandSet(**kwargs),
            DevShellCommandSet(**kwargs),
        ],
    )
    return app_kwargs


def devshell_cmdloop():
    """
    Entry point to start the "dev-shell" cmd2 app.
    Used in: [tool.poetry.scripts]
    """
    app = DevShellApp(**get_devshell_app_kwargs())
    run_cmd2_app(app)  # Run a cmd2 App as CLI or shell
