@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\windows_download.ps1" -Action Install %*
set "result=%ERRORLEVEL%"
echo.
pause
exit /b %result%
