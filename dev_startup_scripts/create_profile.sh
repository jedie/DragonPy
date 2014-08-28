#!/bin/bash

set -x
cd ..
python2 -m cProfile -s cumulative run_all_tests.py | tee profiling.txt