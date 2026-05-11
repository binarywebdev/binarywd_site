@echo off
REM Деплой binarywd.com: билд + rsync → root@213.199.59.61:/var/www/binarywd.com/dist/
REM Просто двойной клик или 'deploy.bat' в cmd
cd /d "%~dp0"
call npm run deploy
if errorlevel 1 (
  echo.
  echo [DEPLOY FAILED]
  pause
  exit /b 1
)
echo.
echo [DEPLOY DONE] https://binarywd.com/
pause
