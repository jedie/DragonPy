@echo off

title "%~0"

set python=C:\Python27\python.exe
REM ~ set python=D:\pypy-2.3.1-win32\pypy.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

echo on
%python% DragonPy_CLI.py --verbosity=50 --cfg=sbc09 --display_cycle
@pause