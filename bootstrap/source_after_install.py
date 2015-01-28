# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
import subprocess
import os
from bootstrap.source_prefix_code import (
    INST_PYPI, INST_GIT, INST_DEV,
    NORMAL_INSTALLATION,GIT_READONLY_INSTALLATION,DEVELOPER_INSTALLATION
)
from bootstrap_env.bootstrap_install_pip import EnvSubprocess


def after_install(options, home_dir):
    # --- CUT here ---
    """
    called after virtualenv was created and pip/setuptools installed.
    Now we installed requirement libs/packages.
    """
    if options.install_type==INST_PYPI:
        requirements=NORMAL_INSTALLATION
    elif options.install_type==INST_GIT:
        requirements=GIT_READONLY_INSTALLATION
    elif options.install_type==INST_DEV:
        requirements=DEVELOPER_INSTALLATION
    else:
        # Should never happen
        raise RuntimeError("Install type %r unknown?!?" % options.install_type)

    env_subprocess = EnvSubprocess(home_dir) # from bootstrap_env.bootstrap_install_pip

    logfile = os.path.join(env_subprocess.abs_home_dir, "install.log")

    for requirement in requirements:
        sys.stdout.write("\n\nInstall %r:\n" % requirement)
        env_subprocess.call_env_pip(["install", "--log=%s" % logfile, requirement])
        sys.stdout.write("\n")
