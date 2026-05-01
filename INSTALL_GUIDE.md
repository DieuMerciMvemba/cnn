# Guide d'Installation - Système UCC

## 🚀 Installation Automatique

### Option 1: Installation Complète
```bash
# Double-cliquer sur :
install_env.bat
```

### Option 2: Lancement Direct
```bash
# Double-cliquer sur :
launch_ucc.bat
```

## 🔧 Installation Manuel

### 1. Créer l'environnement virtuel
```bash
python -m venv venv
```

### 2. Activer l'environnement
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
```bash
python final\ucc_system.py
```

## 📋 Vérification Installation

### Vérifier Python
```bash
python --version
# Doit afficher Python 3.9+
```

### Vérifier l'environnement
```bash
which python
# Doit pointer vers venv/Scripts/python
```

### Vérifier les dépendances
```bash
pip list
# Vérifier que deepface, opencv-python, etc. sont installés
```

## 🎯 Scripts Disponibles

### install_env.bat
- ✅ Crée l'environnement virtuel
- ✅ Installe toutes les dépendances
- ✅ Vérifie Python
- ✅ Met à jour pip

### launch_ucc.bat
- ✅ Vérifie l'environnement
- ✅ Active l'environnement
- ✅ Lance l'application UCC

### start_ucc_complete.bat
- ✅ Lanceur principal
- ✅ Interface complète
- ✅ Vérification système

## 🔍 Dépannage

### Problèmes courants

#### 1. Python non trouvé
```bash
# Solution: Ajouter Python au PATH
# Réinstaller Python en cochant "Add to PATH"
```

#### 2. Erreur d'activation
```bash
# Solution: Recréer l'environnement
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
```

#### 3. Dépendances manquantes
```bash
# Solution: Réinstaller
pip install -r requirements.txt --force-reinstall
```

#### 4. Erreur TensorFlow
```bash
# Solution: Version compatible
pip install tensorflow==2.12.0
```

## 🎓 Utilisation

### Après installation
1. **Lancer** : `launch_ucc.bat`
2. **Se connecter** : Identifiants par défaut
3. **Configurer** : Paramètres de reconnaissance
4. **Utiliser** : Pointage facial

### Configuration recommandée
- **Modèle** : ArcFace
- **Détecteur** : RetinaFace
- **Anti-spoofing** : Activé
- **Seuil** : 0.85

## 📞 Support

Pour toute question :
- Consulter la documentation dans `docs/`
- Vérifier les logs dans `database/`
- Utiliser les scripts de vérification
