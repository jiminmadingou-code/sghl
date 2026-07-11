@echo off
echo ============================================
echo   SGHL Patient — Build APK Release
echo ============================================
echo.

cd /d "%~dp0..\mobile\patient_app"

echo [1/3] Nettoyage du projet Flutter...
flutter clean

echo.
echo [2/3] Generation de l'APK release...
flutter build apk --release --no-tree-shake-icons

if %ERRORLEVEL% NEQ 0 (
  echo ERREUR: La generation de l'APK a echoue.
  pause
  exit /b 1
)

echo.
echo [3/3] Copie de l'APK vers le site de telechargement...
copy /Y "build\app\outputs\flutter-apk\app-release.apk" "%~dp0public\sghl.apk"

echo.
echo ============================================
echo   APK genere avec succes !
echo   Emplacement : download-site\public\sghl.apk
echo ============================================
echo.
echo Prochaine etape : git add + commit + push
echo Railway va redeploy automatiquement.
echo.
pause
