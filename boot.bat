@echo off
REM Activate the virtual environment
call .venv\Scripts\activate.bat

:retry
REM Run your database seeding command
@REM flask seed

REM Check if the previous command was successful
if %errorlevel% equ 0 goto success

echo Deploy command failed, retrying in 5 secs...
timeout /t 5 /nobreak >nul
goto retry

:success
echo.
echo Database seeded successfully! Starting the Web Server...
echo ===============================================================
REM Run the standard Flask development server instead of gunicorn
set FLASK_DEBUG=1
flask run