@echo off
echo Démarrage du Système de Pointage UCC
echo ================================
cd /d "%~dp0"

echo Vérification de l'environnement Python...
python --version
if %errorlevel% neq 0 (
    echo Python non trouvé. Tentative avec venv...
    if exist venv\Scripts\activate (
        call venv\Scripts\activate
    ) else (
        echo Environnement Python non configuré. Veuillez installer Python ou créer venv.
        pause
        exit /b 1
    )
)

echo Lancement du système UCC...
python final\main.py
pause
