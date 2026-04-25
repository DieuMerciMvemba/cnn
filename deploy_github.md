# COMMANDES GIT POUR DÉPLOYER LE PROJET

## 🚀 Initialisation et premier push

```bash
# 1. Créer le README
echo "# cnnsystem" >> README.md

# 2. Initialiser Git
git init

# 3. Ajouter le README
git add README.md

# 4. Premier commit
git commit -m "first commit"

# 5. Renommer la branche en main
git branch -M main

# 6. Ajouter le remote GitHub
git remote add origin https://github.com/Dieudonne-Kalenda24/cnnsystem.git

# 7. Pousser sur GitHub
git push -u origin main
```

## 📁 Ajouter tous les fichiers du projet

```bash
# Ajouter tous les fichiers
git add .

# Commit avec tous les fichiers
git commit -m "Ajout projet complet UCC - reconnaissance faciale"

# Pousser tout sur GitHub
git push origin main
```

## 🎯 Commande complète (une seule fois)

```bash
echo "# cnnsystem" >> README.md && 
git init && 
git add . && 
git commit -m "Projet complet UCC - reconnaissance faciale avec DeepFace" && 
git branch -M main && 
git remote add origin https://github.com/Dieudonne-Kalenda24/cnnsystem.git && 
git push -u origin main
```

## 📋 Structure qui sera poussée

```
cnnsystem/
├── README.md                     # Description du projet
├── Dataset/                      # Images de référence (21 fichiers)
├── docs/                         # Documentation académique
├── facile/                       # Code source principal
├── venv/                         # Environnement (optionnel)
├── requirements.txt               # Dépendances
├── analyse_complete.md           # Analyse du projet
└── .gitignore                   # Fichiers à ignorer
```

## 🚨 Important : Créer .gitignore

```bash
# Créer .gitignore pour éviter les fichiers inutiles
echo "venv/" > .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".deepface/" >> .gitignore
echo "*.db" >> .gitignore
echo "attendance.csv" >> .gitignore
echo "students.csv" >> .gitignore
echo "rapport_*.txt" >> .gitignore
```

## 🎯 Script de déploiement complet

```bash
#!/bin/bash

# Script de déploiement du projet UCC sur GitHub

echo "🚀 Déploiement du projet cnnsystem..."

# 1. Créer README
echo "# cnnsystem
Système de Reconnaissance Faciale pour Pointage Automatique UCC

## 🎯 Objectif
Mise en place d'un système de reconnaissance faciale basé sur les réseaux de neurones convolutifs pour le pointage automatique des étudiants.

## 📁 Structure
- Dataset/ : Images de référence pour reconnaissance
- facile/ : Code source principal
- docs/ : Documentation académique
- venv/ : Environnement virtuel

## 🚀 Installation
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 🎮 Utilisation
\`\`\`bash
python facile/pointage_stable.py
\`\`\`
" > README.md

# 2. Créer .gitignore
echo "venv/
*.pyc
__pycache__/
.deepface/
*.db
attendance.csv
students.csv
rapport_*.txt" > .gitignore

# 3. Initialiser Git
git init

# 4. Ajouter tous les fichiers
git add .

# 5. Commit
git commit -m "🎓 Projet complet UCC - reconnaissance faciale avec DeepFace"

# 6. Configurer remote
git remote add origin https://github.com/Dieudonne-Kalenda24/cnnsystem.git

# 7. Pousser sur GitHub
git branch -M main
git push -u origin main

echo "✅ Projet déployé avec succès !"
echo "🌐 Lien : https://github.com/Dieudonne-Kalenda24/cnnsystem"
```

## 🔧 Utilisation

1. **Copiez-coller** les commandes ci-dessus
2. **Exécutez** dans le dossier `cnn-system`
3. **Patientez** pendant le push
4. **Vérifiez** sur GitHub

---

**Votre projet sera disponible sur :** https://github.com/Dieudonne-Kalenda24/cnnsystem 🚀
