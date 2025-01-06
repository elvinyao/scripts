@echo off
setlocal enabledelayedexpansion

set count=0
set exclude_count=0
set message=

for /f "tokens=1,2 delims=," %%a in ("location.ini") do (
    set "key=%%a"
    
    if "!key:~0,14!"=="excludelocation[" (
        set /a exclude_count+=1
        set excludelocation[!exclude_count!]=%%b
        set !key!=%%b
    ) else if "!key:~0,8!"=="location[" (
        set /a count+=1
        set %%a=%%b
        set message=!message!!count!:%%b^^ ^^
        set lastValue=%%b
    )
)
set /a max_location=%count%
set /a max_excludelocation=%exclude_count%


@echo off
setlocal enabledelayedexpansion

set "check_value=cc"
set "is_excluded=0"

if %max_excludelocation% EQU 0 (
    set "is_excluded=0"
    goto :found
)

for /l %%i in (1,1,%max_excludelocation%) do (
    if "!excludelocation[%%i]!"=="%check_value%" (
        set "is_excluded=1"
        goto :found
    )
)

:found
if %is_excluded%==1 (
    echo Location is excluded
) else (
    echo Location is not excluded
)
