@echo off

title "%~0"

set python=C:\Python27\python.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)
:loop
    echo on
    cls
    %python% setup.py test
    REM ~ %python% -m unittest discover
    @echo off
    pause
goto:loop