#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import subprocess
import sys
import unittest

CLI = os.path.normpath(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "..", "DragonPy_CLI.py"
    )
)


class CLITestCase(unittest.TestCase):
    """
    TODO: Do more than this simple tests
    """

    def _get(self, *args):
        cmd_args = [
            sys.executable,
            CLI
        ]
        cmd_args += args
        # print("\nStartup CLI with: %s" % " ".join(cmd_args[1:]))

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

    def test_exists(self):
        self.assertTrue(
            os.path.isfile(CLI), "CLI file not found here: %s" % CLI
        )

    def test_main_help(self):
        cli_out, cli_err = self._get("--help")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "Usage: DragonPy_CLI.py [OPTIONS] COMMAND [ARGS]...",
            "--machine [CoCo2b|Dragon32|Dragon64|Multicomp6809|Vectrex|sbc09]",
            "Commands:",
            "benchmark  Run a 6809 Emulation benchmark",
            "editor     Run only the BASIC editor",
            "log_list   List all exiting loggers and exit.",
            "run        Run a machine emulation",
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
            "Usage: DragonPy_CLI.py run [OPTIONS]",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)

    def test_editor_help(self):
        cli_out, cli_err = self._get("editor", "--help")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "Usage: DragonPy_CLI.py editor [OPTIONS]",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)

    def test_benchmark_help(self):
        cli_out, cli_err = self._get("benchmark", "--help")
        #        print(cli_out)
        #        print(cli_err)
        self.assertInMultiline([
            "Usage: DragonPy_CLI.py benchmark [OPTIONS]",
        ], cli_out)

        errors = ["Error", "Traceback"]
        self.assertNotInMultiline(errors, cli_out)
        self.assertNotInMultiline(errors, cli_err)


if __name__ == '__main__':
    unittest.main(verbosity=2)
