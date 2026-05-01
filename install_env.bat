@echo off
echo ========================================
echo    Installation Environnement Python UCC
echo ========================================
echo.

echo [1/5] Verification Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installe ou pas dans le PATH
    echo Veuillez installer Python 3.9+ depuis https://python.org
    pause
    exit /b 1
)

echo.
echo [2/5] Creation environnement virtuel...
if exist venv (
    echo ✅ L'environnement virtuel existe deja
    echo Suppression de l'ancien environnement...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la creation de l'environnement virtuel
    pause
    exit /b 1
)

echo ✅ Environnement virtuel cree avec succes

echo.
echo [3/5] Activation de l'environnement...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'activation de l'environnement
    pause
    exit /b 1
)

echo ✅ Environnement active

echo.
echo [4/5] Mise a jour pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la mise a jour de pip
    pause
    exit /b 1
)

echo ✅ Pip mis a jour

echo.
echo [5/5] Installation des dependances...
echo Installation de requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dependances
    echo Tentative d'installation manuelle...
    pip install requests numpy pandas gdown tqdm Pillow opencv-python tensorflow keras flask flask_cors mtcnn retina-face dlib deepface matplotlib reportlab openpyxl
    if %errorlevel% neq 0 (
        echo ❌ Erreur lors de l'installation manuelle
        pause
        exit /b 1
    )
)

echo ✅ Dependances installees avec succes

echo.
echo ========================================
echo ✅ INSTALLATION TERMINEE AVEC SUCCES !
echo ========================================
echo.
echo Pour lancer l'application :
echo 1. Assurez-vous que l'environnement est active : venv\Scripts\activate
echo 2. Lancez : start_ucc_complete.bat
echo.
echo Ou utilisez le raccourci : launch_ucc.bat
echo.

pause
