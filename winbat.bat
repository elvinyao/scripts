@echo off
setlocal enabledelayedexpansion

:: Define the root directory (current directory in this case)
set "rootDir=%CD%"

:: Define the directories to check
set "directories=ini log"

:: Define the files to check in the ini directory
set "iniFiles=location.ini matter.ini"

:: Function to check and create directory
:CheckAndCreateDir
if not exist "%rootDir%\%~1" (
    mkdir "%rootDir%\%~1"
    echo Created directory: %~1
) else (
    echo Directory already exists: %~1
)
goto :eof

:: Function to check and create file
:CheckAndCreateFile
if not exist "%rootDir%\ini\%~1" (
    type nul > "%rootDir%\ini\%~1"
    echo Created file: %~1
) else (
    echo File already exists: %~1
)
goto :eof

:: Main script
echo Checking and creating directories and files...

:: Check and create directories
for %%d in (%directories%) do (
    call :CheckAndCreateDir %%d
)

:: Check and create files in the ini directory
for %%f in (%iniFiles%) do (
    call :CheckAndCreateFile %%f
)

echo Script execution completed.
pause

endlocal
