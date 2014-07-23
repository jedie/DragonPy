@echo off

title "%~0"

set python=C:\Python27\python.exe
REM ~ set python=D:\pypy-2.3.1-win32\pypy.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

REM  5:Hardcore  10:DEBUG  20:INFO  30:WARNING  40:ERROR  50:CRITICAL/FATAL
REM ~ set verbosity=5
REM ~ set verbosity=10
REM ~ set verbosity=20
REM ~ set verbosity=30
REM ~ set verbosity=40
set verbosity=50

:loop
    echo on
    cls
    REM ~ %python% DragonPy_CLI.py --verbosity=%verbosity% --cfg=Simple6809 --display_cycle >"%~n0.log"
    %python% DragonPy_CLI.py --verbosity=%verbosity% --cfg=Simple6809 --display_cycle
    @pause
goto:loop
