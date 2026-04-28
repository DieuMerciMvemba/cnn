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

echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate

echo.
echo 🚀 Démarrage du système UCC...
python final\ucc_system.py

echo.
echo Système arrêté. Appuyez sur une touche pour quitter.
pause
