@echo off
if "%INCLUDE%" == "" (
    echo On Windows, BuildMigrator must run in vcvarsall.bat environment. 1>&2
    exit /b 1
)
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%\..\build_migrator" %*
