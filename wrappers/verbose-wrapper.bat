@echo off

rem Command wrapper for build systems that don't support verbose logs

setlocal enabledelayedexpansion

for %%a in (%*) do (
    set "arg=%%a"
    rem Response file found. Print it in `nmake /U` format.
    if "!arg:~0,1!"=="@" (
        set first=true
        for /F "tokens=*" %%A in (!arg:~1!) do (
            if !first! == true (
                echo echo %%A ^> !arg:~1!
                set first=false
            ) else (
                echo echo %%A ^>^> !arg:~1!
            )
        )
    )
)

echo %*

%*
