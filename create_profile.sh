#!/bin/bash

set -x
pypy -m cProfile -s cumulative run_all_tests.py | tee profiling.txt