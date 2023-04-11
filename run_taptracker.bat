@ECHO off

@REM Get script directory, will have \ on the end
SET mypath=%~dp0

@REM Switch to directory, avoid errors with % in path
cd "%mypath%"

@REM Activate venv environment
call ".\venv\Scripts\activate.bat"

@REM Run script
taptracker --gui
