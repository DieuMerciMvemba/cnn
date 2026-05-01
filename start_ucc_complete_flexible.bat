@echo off
title Système de Pointage UCC
echo.
echo ========================================
echo    SYSTÈME DE POINTAGE UCC
echo    Université Catholique du Congo
echo    Reconnaissance Faciale
echo ========================================
echo.

cd /d "%~dp0"

echo 🔄 Vérification de l'environnement Python...
python --version
if %errorlevel% neq 0 (
    echo Python non trouvé. Tentative avec venv...
    if exist venv\Scripts\activate (
        echo 📦 Activation de l'environnement virtuel...
        call venv\Scripts\activate
    ) else (
        echo ❌ Environnement Python non configuré.
        echo 💡 Options :
        echo    - Installer Python et relancer
        echo    - Exécuter install_env.bat
        echo    - Activer votre environnement conda manuellement
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Démarrage du système UCC...
python final\ucc_system.py

echo.
echo Système arrêté. Appuyez sur une touche pour quitter.
pause
