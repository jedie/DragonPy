#!/usr/bin/env python

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import subprocess
import sys
import unittest


CLI = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
    "..", "..", "DragonPy_CLI.py"
))

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
        print("Startup CLI with: %s" % " ".join(cmd_args[1:]))

        p = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        p.wait()
        stdout = p.stdout.read()
        stderr = p.stderr.read()
        return stdout, stderr

    def test_exists(self):
        self.assertTrue(
            os.path.isfile(CLI), "CLI file not found here: %s" % CLI
        )

    def test_main_help(self):
        stdout, stderr = self._get("--help")
#        print(stdout)
#        print(stderr)
        self.assertIn("usage: DragonPy_CLI.py [-h]", stdout)
        self.assertIn("--machine {Vectrex,Dragon32,Dragon64,CoCo2b}", stdout)
        self.assertIn("{run,editor,benchmark}", stdout)
        self.assertNotIn("Error", stdout)
        self.assertNotIn("Traceback", stdout)
        self.assertNotIn("Error", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_run_help(self):
        stdout, stderr = self._get("run", "--help")
#        print(stdout)
#        print(stderr)
        self.assertIn("usage: DragonPy_CLI.py run [-h] [--trace]", stdout)
        self.assertNotIn("Error", stdout)
        self.assertNotIn("Traceback", stdout)
        self.assertNotIn("Error", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_editor_help(self):
        stdout, stderr = self._get("editor", "--help")
#        print(stdout)
#        print(stderr)
        self.assertIn("usage: DragonPy_CLI.py editor [-h]", stdout)
        self.assertNotIn("Error", stdout)
        self.assertNotIn("Traceback", stdout)
        self.assertNotIn("Error", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_benchmark_help(self):
        stdout, stderr = self._get("benchmark", "--help")
#        print(stdout)
#        print(stderr)
        self.assertIn("usage: DragonPy_CLI.py benchmark [-h]", stdout)
        self.assertNotIn("Error", stdout)
        self.assertNotIn("Traceback", stdout)
        self.assertNotIn("Error", stderr)
        self.assertNotIn("Traceback", stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
