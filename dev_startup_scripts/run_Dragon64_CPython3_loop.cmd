@echo off

title "%~nx0"

set python=C:\Python34\python.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

cd..

:loop
    cls
    echo on
    %python% DragonPy_CLI.py --machine=Dragon64 run
    @echo off
    pause
goto:loop