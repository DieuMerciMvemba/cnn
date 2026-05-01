# Système UCC - Reconnaissance Faciale avec Anti-Spoofing

## 🎯 Description

Système complet de reconnaissance faciale avec anti-spoofing avancé pour l'Université Catholique du Congo.

## 🚀 Installation

### 1. Cloner le projet
```bash
git clone <repository-url>
cd cnn-system
```

### 2. Créer l'environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Initialiser la base de données
```bash
python final\database\database.py
```

### 5. Lancer l'application
```bash
start_ucc_complete.bat
```

## 📋 Fonctionnalités

### 🧠 Reconnaissance Faciale
- **5 modèles CNN** : ArcFace, FaceNet, VGG-Face, OpenFace, DeepFace
- **4 détecteurs** : RetinaFace, MTCNN, Dlib HOG, Haar Cascade
- **Haute précision** : Jusqu'à 99.9% avec validation multi-critères

### 🛡️ Anti-Spoofing
- **Détection liveness** : Clignement des yeux
- **Analyse texture** : Photos imprimées
- **Micro-mouvements** : Respiration naturelle
- **Analyse profondeur** : 2D vs 3D

### 📊 Modules Complets
- **Dashboard** : Statistiques en temps réel
- **Pointage** : Reconnaissance avec anti-spoofing
- **Étudiants** : Gestion complète
- **Rapports** : Exports Excel/PDF
- **Paramètres** : Configuration avancée

## ⚙️ Configuration

Les paramètres sont configurables via l'interface :
- Choix du modèle CNN
- Sélection du détecteur
- Paramètres anti-spoofing
- Seuils de confiance

## 📁 Structure

```
cnn-system/
├── final/
│   ├── views/          # Interface graphique
│   ├── services/       # Logique métier
│   ├── database/       # Base de données
│   └── config/         # Configuration
├── Dataset/            # Photos étudiants
├── database/           # Base SQLite
├── docs/              # Documentation
└── requirements.txt   # Dépendances
```

## 🎯 Performance

- **Précision** : 95-99.9% selon configuration
- **Temps de traitement** : 0.5-3 secondes
- **Support** : CPU/GPU
- **Base de données** : SQLite

## 🔧 Dépendances Principales

- OpenCV : Traitement d'images
- DeepFace : Reconnaissance faciale
- MTCNN/RetinaFace : Détection avancée
- TensorFlow/Keras : Deep Learning
- Dlib : Détection faciale
- Matplotlib : Graphiques
- ReportLab : Rapports PDF

## 🎓 Utilisation

1. **Lancer** l'application avec `start_ucc_complete.bat`
2. **Se connecter** avec les identifiants par défaut
3. **Configurer** les paramètres de reconnaissance
4. **Ajouter** les étudiants avec photos
5. **Commencer** le pointage facial

## 🛡️ Sécurité

- Détection anti-spoofing multi-couches
- Validation multi-critères
- Seuils de confiance stricts
- Journalisation des accès

## 📞 Support

Pour toute question ou problème technique, consulter la documentation dans le dossier `docs/`.
