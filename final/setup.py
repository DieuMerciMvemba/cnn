"""
Script d'installation et de test du système UCC
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Vérifier les dépendances requises"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        'tkinter', 'opencv-python', 'deepface', 'pillow', 
        'pandas', 'openpyxl', 'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'opencv-python':
                import cv2
            elif package == 'deepface':
                from deepface import DeepFace
            elif package == 'pillow':
                from PIL import Image
            elif package == 'pandas':
                import pandas
            elif package == 'openpyxl':
                import openpyxl
            elif package == 'reportlab':
                from reportlab.pdfgen import canvas
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """Installer les dépendances manquantes"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installation des {len(missing_packages)} packages manquants...")
    
    for package in missing_packages:
        try:
            print(f"Installation de {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installé")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation {package}: {e}")
            return False
    
    return True

def check_directories():
    """Vérifier/créer les répertoires nécessaires"""
    print("\n📁 Vérification des répertoires...")
    
    required_dirs = [
        'final/database',
        'final/services',
        'final/utils',
        'final/captures',
        'final/student_photos',
        'final/reports',
        'final/logs'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"📁 {directory} créé")
            except Exception as e:
                print(f"❌ Erreur création {directory}: {e}")
                return False
    
    return True

def check_deepface_model():
    """Vérifier si le modèle DeepFace est disponible"""
    print("\n🧠 Vérification du modèle DeepFace...")
    
    model_path = os.path.expanduser("~/.deepface/weights/vgg_face_weights.h5")
    
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✅ Modèle VGG-Face trouvé ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ Modèle VGG-Face non trouvé")
        print("💡 Le modèle sera téléchargé automatiquement au premier lancement")
        return False

def check_dataset():
    """Vérifier le dataset d'images"""
    print("\n📸 Vérification du dataset...")
    
    dataset_path = "final/Dataset"
    
    if os.path.exists(dataset_path):
        image_files = [f for f in os.listdir(dataset_path) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        print(f"✅ Dataset trouvé: {len(image_files)} images")
        return True
    else:
        print("❌ Dataset non trouvé")
        return False

def test_database():
    """Tester la base de données"""
    print("\n💾 Test de la base de données...")
    
    try:
        sys.path.append('final')
        from database.database import DatabaseUCC
        
        db = DatabaseUCC()
        db.init_facultes()
        db.create_admin_user()
        
        # Test basique
        facultes = db.get_facultes()
        promotions = db.get_promotions()
        
        print(f"✅ Base de données fonctionnelle")
        print(f"   - {len(facultes)} facultés")
        print(f"   - {len(promotions)} promotions")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def test_camera():
    """Tester la caméra"""
    print("\n📷 Test de la caméra...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Caméra fonctionnelle ({frame.shape[1]}x{frame.shape[0]})")
                cap.release()
                return True
            else:
                print("❌ Caméra ne peut pas capturer d'image")
                cap.release()
                return False
        else:
            print("❌ Caméra non disponible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur caméra: {e}")
        return False

def create_startup_script():
    """Créer un script de démarrage"""
    print("\n🚀 Création du script de démarrage...")
    
    script_content = '''@echo off
echo Démarrage du Système de Pointage UCC
echo ================================
cd /d "%~dp0"
venv\\Scripts\\activate
python final\\main.py
pause
'''
    
    try:
        with open('start_ucc.bat', 'w') as f:
            f.write(script_content)
        print("✅ Script start_ucc.bat créé")
        return True
    except Exception as e:
        print(f"❌ Erreur création script: {e}")
        return False

def main():
    """Fonction principale d'installation"""
    print("=" * 60)
    print("🎓 INSTALLATION SYSTÈME DE POINTAGE UCC")
    print("=" * 60)
    
    # Étapes d'installation
    steps = [
        ("Dépendances", check_dependencies, install_dependencies),
        ("Répertoires", check_directories, None),
        ("Base de données", test_database, None),
        ("Caméra", test_camera, None),
        ("Dataset", check_dataset, None),
        ("Modèle DeepFace", check_deepface_model, None),
        ("Script démarrage", create_startup_script, None)
    ]
    
    all_passed = True
    
    for step_name, check_func, install_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        
        if install_func:
            missing = check_func()
            if missing:
                if not install_func(missing):
                    all_passed = False
                    continue
        else:
            if not check_func():
                all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 INSTALLATION RÉUSSIE!")
        print("\n📋 Prochaines étapes:")
        print("1. Double-cliquez sur 'start_ucc.bat' pour démarrer")
        print("2. Ou lancez: python final/main.py")
        print("3. Login par défaut: admin / admin123")
        print("\n🌐 Le système est prêt pour l'UCC!")
    else:
        print("❌ INSTALLATION INCOMPLÈTE")
        print("\n🔧 Veuillez corriger les erreurs ci-dessus")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()
