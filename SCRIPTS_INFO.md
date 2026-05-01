# Scripts de Lancement Flexibles - Système UCC

## 🎯 Scripts Disponibles

### 📦 Pour utilisateurs avec environnement virtuel
- **install_env.bat** - Installation complète venv
- **launch_ucc.bat** - Lancement avec venv obligatoire

### 🔄 Pour utilisateurs flexibles
- **start_ucc_flexible.bat** - Lancement avec environnement existant
- **start_ucc_complete_flexible.bat** - Lancement complet flexible

### 🚀 Scripts originaux (conservés)
- **start_ucc.bat** - Version originale
- **start_ucc_complete.bat** - Version complète originale

## 🎯 Utilisation avec Conda/Env Personnalisé

### Option 1: Script flexible
```bash
# Activer votre environnement conda
conda activate votre_env

# Lancer avec script flexible
start_ucc_flexible.bat
```

### Option 2: Manuel
```bash
# Activer votre environnement
conda activate votre_env

# Lancer directement
python final\ucc_system.py
```

### Option 3: Scripts originaux
```bash
# Les scripts originaux sont conservés
# Ils tentent d'activer venv si disponible
start_ucc.bat
start_ucc_complete.bat
```

## 🔧 Comportement des Scripts Flexibles

### start_ucc_flexible.bat
```batch
@echo off
echo Vérification de l'environnement Python...
python --version
if %errorlevel% neq 0 (
    echo Python non trouvé. Tentative avec venv...
    if exist venv\Scripts\activate (
        call venv\Scripts\activate
    ) else (
        echo Environnement Python non configuré.
        pause
        exit /b 1
    )
)
python final\main.py
```

### start_ucc_complete_flexible.bat
```batch
@echo off
echo Vérification de l'environnement Python...
python --version
if %errorlevel% neq 0 (
    echo Python non trouvé. Tentative avec venv...
    if exist venv\Scripts\activate (
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
python final\ucc_system.py
```

## 🎓 Recommandations

### Pour débutants
```bash
install_env.bat
launch_ucc.bat
```

### Pour utilisateurs avancés
```bash
conda activate votre_env
start_ucc_flexible.bat
```

### Pour déploiement
```bash
start_ucc_complete_flexible.bat
```

## 📋 Avantages

### ✅ Flexibilité
- Utilise environnement Python existant
- Compatible avec conda, venv, system Python
- Messages clairs et options multiples

### 🚀 Simplicité
- Pas besoin de modifier l'environnement existant
- Scripts originaux conservés
- Plusieurs options de lancement

### 🎯 Compatibilité
- Fonctionne avec tous les environnements Python
- Ne force pas l'utilisation de venv
- Respect les configurations existantes
