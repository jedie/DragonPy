#!/bin/bash

cd ..

while true
do
    (
        set -x
        clear
        python2 DragonPy_CLI.py editor
    )
    echo
    read -n1 -p "Press any key to restart" __
    echo
done