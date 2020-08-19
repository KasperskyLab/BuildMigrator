@echo off
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%\..\merge_cmake\merge_cmake.py" %*
