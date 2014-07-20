#!/bin/bash

(
    set -x
    python2 DragonPy_CLI.py --cfg=sbc09
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
        echo "input, don't know"
        ;;
esac
echo
read -n1 -P "ENTER" ENTER