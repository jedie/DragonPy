@echo off

title "%~0"

set python=C:\Python34\python.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

cd..

:loop
    echo on
    %python% -OO DragonPy_CLI.py benchmark --loops 10
    @echo off
    pause
goto:loop