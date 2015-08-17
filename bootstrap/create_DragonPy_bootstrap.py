#!/usr/bin/env python
# coding: utf-8

import os

from bootstrap_env.generate_bootstrap import generate_bootstrap, \
    INSTALL_PIP_MARK, get_code
from bootstrap_env.utils.pip_utils import requirements_definitions

REQ_FILENAMES=(
    "normal_installation.txt",
    "git_readonly_installation.txt",
    "developer_installation.txt",
)

BASE_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__)))

PREFIX_SCRIPT=os.path.abspath(os.path.join(BASE_PATH, "source_prefix_code.py"))

REQ_BASE_PATH=os.path.abspath(os.path.join(BASE_PATH, "..", "requirements"))
print("requirement files path: %r" % REQ_BASE_PATH)


if __name__ == '__main__':
    prefix_code = "\n".join([
        requirements_definitions(REQ_BASE_PATH, REQ_FILENAMES),
        get_code(PREFIX_SCRIPT, INSTALL_PIP_MARK),
    ])

    generate_bootstrap(
        out_filename=os.path.join("..", "boot_dragonpy.py"),
        add_extend_parser="source_extend_parser.py",
        add_adjust_options="source_adjust_options.py",
        add_after_install="source_after_install.py",
        cut_mark="# --- CUT here ---",
        prefix=prefix_code, # Optional code that will be inserted before extend_parser() code part.
        suffix=None, # Optional code that will be inserted after after_install() code part.
    )