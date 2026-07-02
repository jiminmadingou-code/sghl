@echo off
echo ================================================
echo   DIGNE HOSPITAL - SGHL - Demarrage complet
echo ================================================
echo.

:: Demarrer le backend Django
echo [1/2] Demarrage du backend Django (port 8000)...
start "SGHL Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\python manage.py runserver 0.0.0.0:8000"

timeout /t 3 /nobreak > nul

:: Demarrer le frontend Vue
echo [2/2] Demarrage du frontend Vue.js (port 5173)...
start "SGHL Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================================
echo   Application disponible sur :
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/api/v1/docs
echo ================================================
echo.
echo Pour configurer l'envoi d'emails reels :
echo   Editez backend\.env
echo   Remplissez EMAIL_HOST_USER et EMAIL_HOST_PASSWORD
echo ================================================
pause
