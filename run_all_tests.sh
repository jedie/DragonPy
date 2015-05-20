#!/bin/bash

# https://github.com/jedie/DragonPy

source ../../bin/activate

set -x
python -m unittest discover --verbose
