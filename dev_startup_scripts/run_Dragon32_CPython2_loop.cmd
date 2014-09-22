@echo off

title "%~0"

set python=C:\Python27\python.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

cd..

:loop
    cls
    echo on
    %python% -3 DragonPy_CLI.py --machine=Dragon32 run
    @echo off
    pause
goto:loop