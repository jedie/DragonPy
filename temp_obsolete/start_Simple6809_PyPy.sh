#!/bin/bash

(
    set -x
    ~/pypy-2.3.1/bin/pypy DragonPy_CLI.py --verbosity=50 --cfg=Simple6809 --display_cycle
)
echo
read -n1 -p "Start bash? [y,n]" doit
echo
case $doit in
    y|Y)
        bash -i
        exit 0
        ;;
    n|N)
        echo "bye bye"
        ;;
    *)
        echo "input, don't know, bye."
        ;;
esac