"""
Service Détection Visage Avancé - Système UCC
Support de multiples détecteurs : Haar, MTCNN, RetinaFace, Dlib
"""

import cv2
import numpy as np
import time
from typing import List, Tuple, Dict, Optional

try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    MTCNN_AVAILABLE = False

try:
    from retinaface import RetinaFace
    RETINAFACE_AVAILABLE = True
except ImportError:
    RETINAFACE_AVAILABLE = False

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False

class AdvancedFaceDetector:
    def __init__(self, detector_type='auto'):
        self.detector_type = detector_type
        self.current_detector = None
        self.detectors = {}
        
        # Initialiser les détecteurs disponibles
        self.init_detectors()
        
        # Choisir le meilleur détecteur disponible
        self.auto_select_detector()
        
        print(f"Détecteur de visage initialisé: {self.detector_type}")
    
    def init_detectors(self):
        """Initialiser tous les détecteurs disponibles"""
        
        # 1. Haar Cascade (toujours disponible)
        try:
            self.detectors['haar'] = {
                'detector': cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                ),
                'precision': 0.88,
                'speed': 10,  # ms
                'size': 2,    # MB
                'available': True
            }
            print("✅ Haar Cascade initialisé")
        except Exception as e:
            print(f"❌ Erreur Haar Cascade: {e}")
        
        # 2. MTCNN (si disponible)
        if MTCNN_AVAILABLE:
            try:
                self.detectors['mtcnn'] = {
                    'detector': MTCNN(),
                    'precision': 0.96,
                    'speed': 50,  # ms
                    'size': 50,   # MB
                    'available': True
                }
                print("✅ MTCNN initialisé")
            except Exception as e:
                print(f"❌ Erreur MTCNN: {e}")
        
        # 3. RetinaFace (si disponible)
        if RETINAFACE_AVAILABLE:
            try:
                self.detectors['retinaface'] = {
                    'detector': RetinaFace,
                    'precision': 0.98,
                    'speed': 80,  # ms
                    'size': 100,  # MB
                    'available': True
                }
                print("✅ RetinaFace initialisé")
            except Exception as e:
                print(f"❌ Erreur RetinaFace: {e}")
        
        # 4. Dlib HOG (si disponible)
        if DLIB_AVAILABLE:
            try:
                self.detectors['dlib'] = {
                    'detector': dlib.get_frontal_face_detector(),
                    'precision': 0.93,
                    'speed': 25,  # ms
                    'size': 10,   # MB
                    'available': True
                }
                print("✅ Dlib HOG initialisé")
            except Exception as e:
                print(f"❌ Erreur Dlib: {e}")
    
    def auto_select_detector(self):
        """Sélectionner automatiquement le meilleur détecteur disponible"""
        
        if self.detector_type == 'auto':
            # Ordre de priorité : RetinaFace > MTCNN > Dlib > Haar
            priority = ['retinaface', 'mtcnn', 'dlib', 'haar']
            
            for detector_name in priority:
                if detector_name in self.detectors and self.detectors[detector_name]['available']:
                    self.current_detector = detector_name
                    self.detector_type = detector_name
                    break
        else:
            # Utiliser le détecteur spécifié
            if self.detector_type in self.detectors and self.detectors[self.detector_type]['available']:
                self.current_detector = self.detector_type
            else:
                # Fallback sur Haar Cascade
                self.current_detector = 'haar'
                self.detector_type = 'haar'
        
        print(f"Détecteur sélectionné: {self.current_detector}")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détecter les visages avec le détecteur actuel"""
        
        if self.current_detector == 'haar':
            return self.detect_haar(image)
        elif self.current_detector == 'mtcnn':
            return self.detect_mtcnn(image)
        elif self.current_detector == 'retinaface':
            return self.detect_retinaface(image)
        elif self.current_detector == 'dlib':
            return self.detect_dlib(image)
        else:
            return []
    
    def detect_haar(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détection avec Haar Cascade"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            faces = self.detectors['haar']['detector'].detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                maxSize=(300, 300)
            )
            
            return [(x, y, w, h) for (x, y, w, h) in faces]
            
        except Exception as e:
            print(f"Erreur détection Haar: {e}")
            return []
    
    def detect_mtcnn(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détection avec MTCNN"""
        try:
            results = self.detectors['mtcnn']['detector'].detect_faces(image)
            
            faces = []
            for result in results:
                x, y, w, h = result['box']
                faces.append((x, y, w, h))
            
            return faces
            
        except Exception as e:
            print(f"Erreur détection MTCNN: {e}")
            return []
    
    def detect_retinaface(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détection avec RetinaFace"""
        try:
            faces = RetinaFace.extract_faces(image, align=True)
            
            result_faces = []
            for face in faces:
                if isinstance(face, dict) and 'facial_area' in face:
                    x, y, w, h = face['facial_area']
                    result_faces.append((x, y, w, h))
            
            return result_faces
            
        except Exception as e:
            print(f"Erreur détection RetinaFace: {e}")
            return []
    
    def detect_dlib(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détection avec Dlib HOG"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.detectors['dlib']['detector'](gray, 1)
            
            return [(face.left(), face.top(), face.width(), face.height()) for face in faces]
            
        except Exception as e:
            print(f"Erreur détection Dlib: {e}")
            return []
    
    def get_detector_info(self) -> Dict:
        """Obtenir les informations du détecteur actuel"""
        if self.current_detector in self.detectors:
            info = self.detectors[self.current_detector].copy()
            info['name'] = self.current_detector
            info['available_detectors'] = list(self.detectors.keys())
            return info
        else:
            return {
                'name': 'none',
                'precision': 0,
                'speed': 0,
                'size': 0,
                'available': False,
                'available_detectors': list(self.detectors.keys())
            }
    
    def switch_detector(self, detector_type: str) -> bool:
        """Changer de détecteur"""
        if detector_type in self.detectors and self.detectors[detector_type]['available']:
            self.current_detector = detector_type
            self.detector_type = detector_type
            print(f"Détecteur changé vers: {detector_type}")
            return True
        else:
            print(f"Détecteur {detector_type} non disponible")
            return False
    
    def benchmark_detectors(self, test_image: np.ndarray, iterations: int = 10) -> Dict:
        """Benchmark tous les détecteurs disponibles"""
        results = {}
        
        for name, detector_info in self.detectors.items():
            if not detector_info['available']:
                continue
            
            # Temporairement changer vers ce détecteur
            original_detector = self.current_detector
            self.current_detector = name
            
            # Mesurer performance
            times = []
            face_counts = []
            
            for _ in range(iterations):
                start_time = time.time()
                faces = self.detect_faces(test_image)
                end_time = time.time()
                
                times.append((end_time - start_time) * 1000)  # ms
                face_counts.append(len(faces))
            
            # Restaurer détecteur original
            self.current_detector = original_detector
            
            results[name] = {
                'avg_time': np.mean(times),
                'avg_faces': np.mean(face_counts),
                'precision': detector_info['precision'],
                'speed': detector_info['speed'],
                'size': detector_info['size']
            }
        
        return results

# Test du service avancé
if __name__ == "__main__":
    detector = AdvancedFaceDetector('auto')
    
    print("=== INFOS DÉTECTEUR AVANCÉ ===")
    info = detector.get_detector_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\nDétecteurs disponibles: {info['available_detectors']}")
