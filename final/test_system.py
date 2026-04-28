"""
Script de test pour vérifier tous les modules du système UCC
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Tester les imports de tous les modules"""
    print("🧪 Test des imports...")
    
    try:
        # Base de données
        from database.database import DatabaseUCC
        print("✅ DatabaseUCC importé")
        
        # Services
        from services.face_recognition import FaceRecognitionUCC
        print("✅ FaceRecognitionUCC importé")
        
        from services.camera_service import CameraServiceUCC
        print("✅ CameraServiceUCC importé")
        
        # Vues
        from views.login import LoginScreen
        print("✅ LoginScreen importé")
        
        from views.portal import PortalScreen
        print("✅ PortalScreen importé")
        
        from views.students import StudentsScreen
        print("✅ StudentsScreen importé")
        
        from views.attendance import AttendanceScreen
        print("✅ AttendanceScreen importé")
        
        from views.organization import OrganizationScreen
        print("✅ OrganizationScreen importé")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False

def test_database():
    """Tester la base de données"""
    print("\n💾 Test de la base de données...")
    
    try:
        from database.database import DatabaseUCC
        
        db = DatabaseUCC()
        db.init_facultes()
        db.create_admin_user()
        
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
        from services.camera_service import CameraServiceUCC
        
        camera = CameraServiceUCC()
        
        if camera.initialize_camera():
            print("✅ Caméra initialisée avec succès")
            camera.stop_capture()
            return True
        else:
            print("❌ Impossible d'initialiser la caméra")
            return False
            
    except Exception as e:
        print(f"❌ Erreur caméra: {e}")
        return False

def test_face_recognition():
    """Tester la reconnaissance faciale"""
    print("\n🧠 Test de la reconnaissance faciale...")
    
    try:
        from services.face_recognition import FaceRecognitionUCC
        
        face_service = FaceRecognitionUCC()
        
        # Données test
        test_students = {
            'test1': {
                'name': 'Test Student',
                'faculte': 'Test Faculté',
                'promotion': 'LICENCE 1',
                'matricule': 'TEST-001',
                'photo_path': 'Dataset/Dieudonne.jpg'  # Utiliser une image existante
            }
        }
        
        face_service.load_student_database(test_students)
        stats = face_service.get_performance_stats()
        
        print("✅ Service reconnaissance faciale fonctionnel")
        print(f"   - Étudiants chargés: {stats['students_loaded']}")
        print(f"   - Détecteur: {'Oui' if stats['detector_loaded'] else 'Non'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur reconnaissance faciale: {e}")
        return False

def main():
    """Test complet du système"""
    print("=" * 60)
    print("🎓 TEST COMPLET SYSTÈME UCC")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Base de données", test_database),
        ("Caméra", test_camera),
        ("Reconnaissance faciale", test_face_recognition)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résultats finaux
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS - SYSTÈME PRÊT !")
        print("\n🚀 Pour démarrer le système:")
        print("   python final/ucc_system.py")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFIEZ LE SYSTÈME")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
