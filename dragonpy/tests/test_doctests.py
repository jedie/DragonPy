from bx_py_utils.test_utils.unittest_utils import BaseDocTests

import basic_editor
import dragonpy
import misc
import PyDC


class DocTests(BaseDocTests):
    def test_doctests(self):
        self.run_doctests(
            modules=(dragonpy, basic_editor, misc, PyDC),
        )
