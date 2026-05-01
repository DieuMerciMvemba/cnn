@echo off
echo ========================================
echo    Lancement Système UCC
echo ========================================
echo.

echo [1/3] Verification environnement...
if not exist venv (
    echo ❌ Environnement virtuel non trouve
    echo Veuillez d'abord executer install_env.bat
    pause
    exit /b 1
)

echo.
echo [2/3] Activation environnement...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'activation
    pause
    exit /b 1
)

echo ✅ Environnement active

echo.
echo [3/3] Lancement application...
echo Demarrage du systeme UCC...
python final\ucc_system.py

if %errorlevel% neq 0 (
    echo ❌ Erreur lors du lancement de l'application
    pause
    exit /b 1
)

echo.
echo ✅ Systeme UCC lance avec succes !

pause
