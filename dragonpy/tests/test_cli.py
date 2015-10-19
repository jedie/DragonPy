#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import subprocess
import unittest

from click.testing import CliRunner

import MC6809

import dragonpy
from dragonpy.core.cli import cli
from dragonpy.utils.starter import run_dragonpy, run_mc6809


class CliTestCase(unittest.TestCase):
    def assert_contains_members(self, members, container):
        for member in members:
            msg = "%r not found in:\n%s" % (member, container)
            # self.assertIn(member, container, msg) # Bad error message :(
            if not member in container:
                self.fail(msg)

    def assert_not_contains_members(self, members, container):
        for member in members:
            if member in container:
                self.fail("%r found in:\n%s" % (member, container))

    def assert_is_help(self, output):
        self.assert_contains_members([
            "Usage: ", " [OPTIONS] COMMAND [ARGS]...", # Don't check "filename": It's cli or cli.py in unittests!

            "DragonPy is a Open source (GPL v3 or later) emulator for the 30 years old",
            "homecomputer Dragon 32 and Tandy TRS-80 Color Computer (CoCo)...",

            "Homepage: https://github.com/jedie/DragonPy",

            "--machine [CoCo2b|Dragon32|Dragon64|Multicomp6809|Simple6809|Vectrex|sbc09]",
            "Commands:",
            "download_roms  Download/Test only ROM files",
            "editor         Run only the BASIC editor",
            "log_list       List all exiting loggers and exit.",
            "nosetests      Run all tests via nose",
            "run            Run a machine emulation",
        ], output)


class TestStarter(CliTestCase):
    """
    Test the "starter functions" that invoke DragonPy / MC6809 via subprocess.
    """
    def _run(self, func, *args, **kwargs):
        p = func(*args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            **kwargs
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

    def _run_dragonpy(self, *args, **kwargs):
        return self._run(run_dragonpy, *args, **kwargs)

    def _run_MC6809(self, *args, **kwargs):
        return self._run(run_mc6809, *args, **kwargs)

    def test_run_dragonpy_version(self):
        cli_out, cli_err = self._run_dragonpy(
            "--version",
            # verbose=True
        )
        self.assertIn(dragonpy.__version__, cli_out)
        self.assertEqual(cli_err, "")

    def test_run_dragonpy_help(self):
        cli_out, cli_err = self._run_dragonpy(
            "--help",
            # verbose=True
        )
        self.assert_is_help(cli_out)
        self.assertEqual(cli_err, "")

    def test_run_MC6809_version(self):
        cli_out, cli_err = self._run_MC6809(
            "--version",
            # verbose=True
        )
        self.assertIn(MC6809.__version__, cli_out)
        self.assertEqual(cli_err, "")

    def test_run_MC6809_help(self):
        cli_out, cli_err = self._run_MC6809(
            "--help",
            # verbose=True
        )
        self.assert_contains_members([
            "Usage: ", " [OPTIONS] COMMAND [ARGS]...", # Don't check "filename": It's cli or cli.py in unittests!
            "Homepage: https://github.com/6809/MC6809",
            "Run a 6809 Emulation benchmark",
        ], cli_out)
        self.assertEqual(cli_err, "")


class CLITestCase(CliTestCase):
    """
    Test the click cli via click.CliRunner().invoke()
    """
    def _invoke(self, *args):
        runner = CliRunner()
        result = runner.invoke(cli, args)

        if result.exit_code != 0:
            msg = (
                "\nstart CLI with: '%s'\n"
                "return code: %r\n"
                " *** output: ***\n"
                "%s\n"
                " *** exception: ***\n"
                "%s\n"
                "****************\n"
            ) % (" ".join(args), result.exit_code, result.output, result.exception)
            self.assertEqual(result.exit_code, 0, msg=msg)

        return result

    def test_main_help(self):
        result = self._invoke("--help")
        #        print(result.output)
        #        print(cli_err)
        self.assert_is_help(result.output)

        errors = ["Error", "Traceback"]
        self.assert_not_contains_members(errors, result.output)

    def test_version(self):
        result = self._invoke("--version")
        self.assertIn(dragonpy.__version__, result.output)

    def test_log_list(self):
        result = self._invoke("log_list")
        #        print(result.output)
        #        print(cli_err)
        self.assert_contains_members([
            "A list of all loggers:",
            "DragonPy.cpu6809",
            "dragonpy.Dragon32.MC6821_PIA",
        ], result.output)

        errors = ["Error", "Traceback"]
        self.assert_not_contains_members(errors, result.output)

    def test_run_help(self):
        result = self._invoke("run", "--help")
        #        print(result.output)
        #        print(cli_err)
        self.assert_contains_members([
            "Usage: cli run [OPTIONS]",
        ], result.output)

        errors = ["Error", "Traceback"]
        self.assert_not_contains_members(errors, result.output)

    def test_editor_help(self):
        result = self._invoke("editor", "--help")
        #        print(result.output)
        #        print(cli_err)
        self.assert_contains_members([
            "Usage: cli editor [OPTIONS]",
        ], result.output)

        errors = ["Error", "Traceback"]
        self.assert_not_contains_members(errors, result.output)

    def test_download_roms(self):
        result = self._invoke("download_roms")
        # print(result.output)
        # print(cli_err)
        self.assert_contains_members([
            "ROM file: d64_ic17.rom",
            "Read ROM file",
            "ROM SHA1:",
            "ok",
            "file size is",
        ], result.output)

        errors = ["Error", "Traceback"]
        self.assert_not_contains_members(errors, result.output)

