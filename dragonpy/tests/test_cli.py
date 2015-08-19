#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
from dragonlib.utils.unittest_utils import TextTestRunner2

import os
import subprocess
import sys
import unittest


CLI = "DragonPy" # entry_points in setup.py !


class CLITestCase(unittest.TestCase):
    """
    TODO: Do more than this simple tests
    """

    def _get(self, *args):
        try:
            VIRTUAL_ENV = os.environ["VIRTUAL_ENV"]
        except KeyError as err:
            # e.g.: started by PyCharm
            cli = os.path.join(os.path.dirname(sys.executable), CLI)
        else:
            cli = os.path.join(VIRTUAL_ENV, "bin", CLI)

        self.assertTrue(os.path.isfile(cli), "CLI file %r not found!" % cli)

        cmd_args = [cli] + list(args)
        # print("\nStartup CLI with: %r" % " ".join(cmd_args))

        p = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        retcode = p.wait()

        cli_out = p.stdout.read()
        p.stdout.close()
        cli_err = p.stderr.read()
        p.stderr.close()

        if retcode != 0:
            msg = (
                "subprocess returned %s.\n"
                " *** stdout: ***\n"
                "%s\n"
                " *** stderr: ***\n"
                "%s\n"
                "****************\n"
            ) % (retcode, cli_out, cli_err)
            self.assertEqual(retcode, 0, msg=msg)

        return cli_out, cli_err

    def assertInMultiline(self, members, container):
        for member in members:
            msg = "%r not found in:\n%s" % (member, container)
            # self.assertIn(member, container, msg) # Bad error message :(
            if not member in container:
                self.fail(msg)

    def assertNotInMultiline(self, members, container):
        for member in members:
            if member in container:
                self.fail("%r found in:\n%s" % (member, container))

    def test_main_help(self):
        cli_out, cli_err = self._get("--help")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "Usage: DragonPy [OPTIONS] COMMAND [ARGS]...",
            "--machine [CoCo2b|Dragon32|Dragon64|Multicomp6809|Vectrex|sbc09]",
            "Commands:",
            "download_roms  Download/Test only ROM files",
            "editor         Run only the BASIC editor",
            "log_list       List all exiting loggers and exit.",
            "run            Run a machine emulation",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)

    def test_log_list(self):
        cli_out, cli_err = self._get("log_list")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "A list of all loggers:",
            "DragonPy.cpu6809",
            "dragonpy.Dragon32.MC6821_PIA",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)

    def test_run_help(self):
        cli_out, cli_err = self._get("run", "--help")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "Usage: DragonPy run [OPTIONS]",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)

    def test_editor_help(self):
        cli_out, cli_err = self._get("editor", "--help")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "Usage: DragonPy editor [OPTIONS]",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)

    def test_download_roms(self):
        cli_out, cli_err = self._get("download_roms")
        # print(cli_out)
        # print(cli_err)
        self.assertInMultiline([
            "ROM file: d64_ic17.rom",
            "Read ROM file",
            "ROM SHA1:",
            "ok",
            "file size is",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)



if __name__ == '__main__':
    unittest.main(
        argv=(
            sys.argv[0],
            # "CLITestCase.test_download_roms",
        ),
        testRunner=TextTestRunner2,
        # verbosity=1,
        verbosity=2,
        failfast=False,
        # failfast=True,
    )
