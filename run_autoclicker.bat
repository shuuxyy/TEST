@echo off
setlocal

REM Launcher for the Windows autoclicker script.
REM Use:
REM   run_autoclicker.bat --gui
REM   run_autoclicker.bat --interval 0.1 --count 100 --button left --delay 3

python "%~dp0autoclicker.py" %*
