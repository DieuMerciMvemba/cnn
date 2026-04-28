@echo off
echo Démarrage du Système de Pointage UCC
echo ================================
cd /d "%~dp0"
venv\Scripts\activate
python final\main.py
pause
