@echo off
setlocal EnableDelayedExpansion

rem Make the API call and store the response in a temporary file
curl -s "http://example.com/api/1" > response.json

rem Extract the status value using findstr and string manipulation
for /f "tokens=2 delims=:}" %%a in ('type response.json ^| findstr "status"') do (
    set "status=%%a"
)

rem Clean up the status value by removing quotes and spaces
set "status=!status:"=!"
set "status=!status: =!"

rem Now status variable contains the value "telecowk"
echo Status is: !status!

rem Clean up temporary file
del response.json

rem Use the status variable as needed
if "!status!"=="telecowk" (
    echo Status is telecowk
)
