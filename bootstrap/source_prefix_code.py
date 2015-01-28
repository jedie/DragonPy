# coding: utf-8


# imports not really needed and just for the editor warning ;)
import os
import sys
import subprocess


# Will be inserted in real bootstrap file ;)
NORMAL_INSTALLATION = None # requirements from normal_installation.txt
GIT_READONLY_INSTALLATION = None # requirements from git_readonly_installation.txt
DEVELOPER_INSTALLATION = None # requirements from developer_installation.txt


# --- CUT here ---

# For choosing the installation type:
INST_PYPI="pypi"
INST_GIT="git_readonly"
INST_DEV="dev"

INST_TYPES=(INST_PYPI, INST_GIT, INST_DEV)
