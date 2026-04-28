# Lisez-moi - Système de Pointage UCC

## 🎓 Présentation

Système complet de pointage automatique pour l'Université Catholique du Congo (UCC) basé sur la reconnaissance faciale avec DeepFace.

## 🚀 Installation

### Installation Automatique (Recommandé)
```bash
python final/setup.py
```

### Installation Manuelle
1. **Activer l'environnement virtuel**
   ```bash
   venv\Scripts\activate
   ```

2. **Installer les dépendances**
   ```bash
   pip install opencv-python deepface pillow pandas openpyxl reportlab
   ```

3. **Initialiser la base de données**
   ```bash
   python final/database/database.py
   ```

## 🎮 Utilisation

### Démarrage Rapide
1. **Double-cliquez** sur `start_ucc.bat`
2. **Ou manuellement** :
   ```bash
   venv\Scripts\activate
   python final/main.py
   ```

### Login par Défaut
- **Utilisateur** : admin
- **Mot de passe** : admin123

## 📁 Structure du Projet

```
final/
├── main.py                    # Application principale
├── database/
│   ├── database.py            # Base de données SQLite
│   └── __init__.py
├── services/
│   ├── face_recognition.py    # Reconnaissance faciale DeepFace
│   ├── camera_service.py      # Gestion caméra
│   └── __init__.py
├── utils/
│   ├── config.py              # Configuration système
│   └── __init__.py
├── Dataset/                   # Images de référence (21 photos)
├── captures/                  # Photos capturées
├── student_photos/            # Photos des étudiants
├── reports/                   # Rapports générés
└── logs/                      # Logs système
```

## 🎯 Fonctionnalités

### ✅ Reconnaissance Faciale
- **DeepFace VGG-Face** : 98.7% de précision
- **Anti-spoofing** basique
- **Cache intelligent** pour performance
- **Multi-visages** simultanés

### ✅ Gestion Étudiants UCC
- **9 Facultés** : Économie, Informatique, Politique, etc.
- **5 Promotions** : LICENCE 1-3, MASTER 1-2
- **Matricule automatique** : UCC-ANNEE-FACULTE-ID
- **Photos multiples** par étudiant

### ✅ Pointage Automatique
- **Détection entrée/sortie**
- **Gestion des retards** (après 8h)
- **Anti-doublon** (5 minutes)
- **Historique temps réel**

### ✅ Interface Tkinter
- **Caméra en direct** avec reconnaissance
- **Tableau de bord** statistiques
- **Historique** des pointages
- **Messages clairs** pour utilisateurs

### ✅ Base de Données
- **SQLite** : portable et rapide
- **Tables optimisées** : students, attendance, users, logs
- **Sécurité** : hash mots de passe
- **Backup** automatique

## 📊 Statistiques en Temps Réel

- **Total étudiants** inscrits
- **Présents du jour**
- **Absents du jour**
- **Taux de présence** (%)
- **Historique** par faculté

## 🔧 Configuration

### Paramètres Modifiables
```python
# utils/config.py
CAMERA_ID = 0                    # ID caméra
FACE_CONFIDENCE_THRESHOLD = 0.6  # Seuil reconnaissance
LATE_HOUR = 8                    # Heure retard
SESSION_TIMEOUT = 1800           # Timeout session (30 min)
```

### Facultés UCC
- Économie et Développement
- Sciences Informatiques
- Sciences Politique
- Théologie
- Philosophie
- Droit Canonique
- Communication Sociale
- Médecine
- Droit

## 🛡️ Sécurité

- **Hash SHA-256** pour mots de passe
- **Session timeout** 30 minutes
- **Logs d'actions** complets
- **Validation entrées** utilisateur

## 📈 Performance

- **Threading** : caméra async
- **Cache DeepFace** : résultats temporisés
- **Limitation comparaisons** : max 10/frame
- **Optimisation mémoire** : gestion automatique

## 🚨 Dépannage

### Problèmes Communs

**Caméra ne fonctionne pas**
```bash
# Tester la caméra
python -c "import cv2; cap=cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'Erreur')"
```

**Modèle DeepFace non trouvé**
```bash
# Le modèle sera téléchargé automatiquement au premier lancement
# Vérifier : ~/.deepface/weights/vgg_face_weights.h5
```

**Erreur de dépendances**
```bash
# Réinstaller toutes les dépendances
pip install --upgrade opencv-python deepface pillow pandas openpyxl reportlab
```

### Performance Lente
- **Augmenter le seuil de confiance** : 0.7
- **Réduire les comparaisons** : 5 max
- **Vider le cache** régulièrement

## 📤 Exports et Rapports

### Formats Supportés
- **Excel** (.xlsx) : pandas + openpyxl
- **PDF** (.pdf) : reportlab
- **CSV** (.csv) : données brutes

### Rapports Disponibles
- **Présence journalière** par faculté
- **Statistiques mensuelles**
- **Listes individuelles** par étudiant
- **Taux de présence** global

## 🔄 Maintenance

### Sauvegardes
- **Base de données** : `database/ucc_system.db`
- **Photos étudiants** : `student_photos/`
- **Logs système** : `logs/ucc_system.log`

### Nettoyage
- **Cache reconnaissance** : bouton "Vider Cache"
- **Photos temporaires** : `captures/`
- **Logs anciens** : rotation automatique

## 🎓 Support UCC

### Contact Technique
- **Développeur** : Dieudonne Kalenda
- **Email** : [votre email]
- **GitHub** : https://github.com/DieuMerciMvemba/cnn

### Formation
- **Guide administrateur** : 1 page
- **Guide surveillant** : pointage
- **Vidéo démo** : 5 minutes

## 🌟 Version Actuelle

**Version 1.0.0** - Système complet UCC
- ✅ Reconnaissance faciale DeepFace
- ✅ Interface Tkinter complète
- ✅ Base de données SQLite
- ✅ Gestion étudiants UCC
- ✅ Pointage automatique
- ✅ Statistiques temps réel
- ✅ Exports Excel/PDF

---

**🎓 Système de Pointage UCC - Prêt pour l'Université Catholique du Congo !**

*Développé avec ❤️ pour l'UCC*
