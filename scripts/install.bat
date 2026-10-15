@echo off
setlocal EnableExtensions

rem Installs every skill in this repo's .claude\skills folder into the
rem user-level Claude Code skills folder (%USERPROFILE%\.claude\skills),
rem so the skills are available in every project.
rem
rem Usage:  scripts\install.bat [--no-pause]

for %%I in ("%~dp0..") do set "REPO_ROOT=%%~fI"
set "SRC=%REPO_ROOT%\.claude\skills"
set "DEST=%USERPROFILE%\.claude\skills"

if not exist "%SRC%\" (
  echo [ERROR] Skills folder not found: "%SRC%"
  goto :fail
)

if not exist "%DEST%\" mkdir "%DEST%"
if not exist "%DEST%\" (
  echo [ERROR] Could not create "%DEST%"
  goto :fail
)

set "COUNT=0"
for /d %%S in ("%SRC%\*") do (
  if exist "%%S\SKILL.md" (
    echo Installing %%~nxS ...
    robocopy "%%S" "%DEST%\%%~nxS" /E /NFL /NDL /NJH /NJS /NP >nul
    if errorlevel 8 (
      echo [ERROR] Failed to copy %%~nxS
      goto :fail
    )
    set /a COUNT+=1
  )
)

echo.
echo Installed %COUNT% skill^(s^) into "%DEST%".

rem The hyperframes skill drives the "npx hyperframes" CLI.
where npx >nul 2>&1
if errorlevel 1 (
  echo [WARN] npx was not found on PATH. Install Node.js from https://nodejs.org
  echo        to use the hyperframes CLI commands.
)

echo Restart Claude Code to pick up the new skills.
call :maybe_pause %1
exit /b 0

:fail
call :maybe_pause %1
exit /b 1

:maybe_pause
if /i not "%~1"=="--no-pause" pause
exit /b 0
