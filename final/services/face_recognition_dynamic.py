"""
Service de reconnaissance faciale dynamique - Système UCC
Choisit automatiquement le modèle selon les paramètres
"""

import cv2
import os
import time
import numpy as np
from deepface import DeepFace
import threading
from datetime import datetime
import json

class FaceRecognitionDynamic:
    def __init__(self, settings_file="final/config/settings.json"):
        self.settings_file = settings_file
        self.students_db = {}
        self.face_cascade = None
        self.recognition_cache = {}
        self.cache_timeout = 5
        self.last_recognition_time = {}
        self.min_face_size = (64, 64)
        self.current_model = None
        self.current_service = None
        
        # Charger les paramètres
        self.load_settings()
        
        # Initialiser le détecteur de visage
        self.init_face_detector()
        
        # Initialiser le service de reconnaissance
        self.init_recognition_service()
        
        print(f"Service reconnaissance faciale dynamique initialisé avec {self.current_model}")
    
    def load_settings(self):
        """Charger les paramètres depuis le fichier"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                recognition_settings = settings.get('recognition', {})
                self.current_model = recognition_settings.get('model', 'VGG-Face')
                self.threshold = recognition_settings.get('threshold', 0.4)
                self.detection_threshold = recognition_settings.get('detection_threshold', 0.95)
                
                print(f"Paramètres chargés: modèle={self.current_model}, seuil={self.threshold}")
            else:
                # Valeurs par défaut
                self.current_model = 'VGG-Face'
                self.threshold = 0.4
                self.detection_threshold = 0.95
                print("Utilisation des paramètres par défaut")
                
        except Exception as e:
            print(f"Erreur chargement paramètres: {e}")
            self.current_model = 'VGG-Face'
            self.threshold = 0.4
            self.detection_threshold = 0.95
    
    def init_face_detector(self):
        """Initialiser le détecteur de visage"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if self.face_cascade.empty():
                raise Exception("Impossible de charger Haar Cascade")
            print("Détecteur de visage initialisé")
        except Exception as e:
            print(f"Erreur initialisation détecteur: {e}")
            self.face_cascade = None
    
    def init_recognition_service(self):
        """Initialiser le service de reconnaissance selon le modèle"""
        try:
            if self.current_model == 'ArcFace':
                self.init_arcface_service()
            elif self.current_model == 'Facenet':
                self.init_facenet_service()
            else:
                self.init_vgg_service()
                
            print(f"Service {self.current_model} initialisé")
            
        except Exception as e:
            print(f"Erreur initialisation service {self.current_model}: {e}")
            # Fallback sur VGG-Face
            self.current_model = 'VGG-Face'
            self.init_vgg_service()
    
    def init_arcface_service(self):
        """Initialiser le service ArcFace"""
        # Paramètres spécifiques à ArcFace
        self.cache_timeout = 3
        self.min_face_size = (80, 80)
        self.distance_metric = 'cosine'
        self.detector_backend = 'retinaface'
        self.confidence_threshold = 0.7
        
        # Importer le service ArcFace
        try:
            from .face_recognition_arcface import FaceRecognitionUCC_ArcFace
            self.current_service = FaceRecognitionUCC_ArcFace()
        except ImportError:
            print("ArcFace non disponible, fallback sur VGG-Face")
            self.init_vgg_service()
    
    def init_facenet_service(self):
        """Initialiser le service FaceNet"""
        # Paramètres spécifiques à FaceNet
        self.cache_timeout = 4
        self.min_face_size = (70, 70)
        self.distance_metric = 'euclidean_l2'
        self.detector_backend = 'mtcnn'
        self.confidence_threshold = 0.65
        
        # Importer le service FaceNet (simulé ici)
        self.current_service = self  # Utiliser le service de base
    
    def init_vgg_service(self):
        """Initialiser le service VGG-Face (par défaut)"""
        # Paramètres VGG-Face
        self.cache_timeout = 5
        self.min_face_size = (64, 64)
        self.distance_metric = 'cosine'
        self.detector_backend = 'opencv'
        self.confidence_threshold = 0.6
        
        self.current_service = self  # Utiliser le service de base
    
    def load_student_database(self, students_data):
        """Charger la base de données des étudiants"""
        self.students_db = students_data
        if hasattr(self.current_service, 'load_student_database'):
            self.current_service.load_student_database(students_data)
        print(f"Base chargée: {len(students_data)} étudiants pour {self.current_model}")
    
    def detect_faces(self, frame):
        """Détecter les visages dans une image"""
        if self.face_cascade is None:
            return []
        
        try:
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Paramètres selon le modèle
            scale_factor = 1.05 if self.current_model == 'ArcFace' else 1.1
            min_neighbors = 6 if self.current_model == 'ArcFace' else 5
            
            # Détecter les visages
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=self.min_face_size
            )
            
            return faces
        except Exception as e:
            print(f"Erreur détection visage: {e}")
            return []
    
    def extract_face_roi(self, frame, face_coords):
        """Extraire la région d'intérêt du visage"""
        x, y, w, h = face_coords
        
        # S'assurer que les coordonnées sont valides
        x = max(0, x)
        y = max(0, y)
        w = min(w, frame.shape[1] - x)
        h = min(h, frame.shape[0] - y)
        
        if w < self.min_face_size[0] or h < self.min_face_size[1]:
            return None
        
        face_roi = frame[y:y+h, x:x+w]
        
        # Redimensionner selon le modèle
        if self.current_model == 'ArcFace':
            face_roi = cv2.resize(face_roi, (112, 112))
        elif self.current_model == 'Facenet':
            face_roi = cv2.resize(face_roi, (160, 160))
        else:
            face_roi = cv2.resize(face_roi, (224, 224))
        
        return face_roi
    
    def recognize_face(self, face_image, student_id_hint=None):
        """Reconnaître un visage avec le modèle actuel"""
        current_time = time.time()
        
        # Vérifier le cache
        cache_key = f"{id(face_image)}_{student_id_hint}_{self.current_model}"
        if (cache_key in self.recognition_cache and 
            current_time - self.recognition_cache[cache_key]['time'] < self.cache_timeout):
            return self.recognition_cache[cache_key]['result']
        
        try:
            # Limiter le nombre de comparaisons selon le modèle
            max_comparisons = 20 if self.current_model == 'ArcFace' else 10
            students_to_compare = list(self.students_db.items())[:max_comparisons]
            
            best_match = None
            best_score = 0
            
            for student_id, student_info in students_to_compare:
                if student_id_hint and student_id != student_id_hint:
                    continue
                
                photo_path = student_info.get('photo_path')
                if not photo_path or not os.path.exists(photo_path):
                    continue
                
                try:
                    # Comparaison avec le modèle actuel
                    result = DeepFace.verify(
                        face_image,
                        photo_path,
                        model_name=self.current_model,
                        detector_backend='skip',
                        distance_metric=self.distance_metric,
                        enforce_detection=False
                    )
                    
                    if result['verified']:
                        distance = result.get('distance', 0)
                        
                        # Conversion selon le modèle
                        if self.distance_metric == 'cosine':
                            score = 1 - distance
                        else:
                            score = 1 / (1 + distance)
                        
                        if score > best_score and score > self.confidence_threshold:
                            best_score = score
                            best_match = {
                                'student_id': student_id,
                                'name': student_info.get('name', ''),
                                'faculte': student_info.get('faculte', ''),
                                'promotion': student_info.get('promotion', ''),
                                'matricule': student_info.get('matricule', ''),
                                'confidence': score,
                                'model': self.current_model
                            }
                
                except Exception as e:
                    continue
            
            # Mettre en cache le résultat
            result = best_match if best_match and best_score > self.confidence_threshold else None
            self.recognition_cache[cache_key] = {
                'result': result,
                'time': current_time
            }
            
            return result
            
        except Exception as e:
            print(f"Erreur reconnaissance {self.current_model}: {e}")
            return None
    
    def process_frame(self, frame):
        """Traiter une frame complète"""
        results = []
        
        # Détecter les visages
        faces = self.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            # Extraire le ROI du visage
            face_roi = self.extract_face_roi(frame, (x, y, w, h))
            
            if face_roi is None:
                continue
            
            # Reconnaître le visage
            recognition = self.recognize_face(face_roi)
            
            results.append({
                'bbox': (x, y, w, h),
                'recognition': recognition,
                'confidence': recognition['confidence'] if recognition else 0
            })
        
        return results
    
    def draw_results(self, frame, results):
        """Dessiner les résultats sur la frame"""
        for result in results:
            x, y, w, h = result['bbox']
            recognition = result['recognition']
            
            if recognition:
                # Vert pour reconnu
                color = (0, 255, 0)
                model_info = f"[{recognition['model']}]"
                label = f"{recognition['name']} {model_info} ({recognition['confidence']:.2f})"
            else:
                # Rouge pour non reconnu
                color = (0, 0, 255)
                label = f"Non reconnu [{self.current_model}]"
            
            # Dessiner le rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Dessiner le label
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                         (x + label_size[0], y), color, -1)
            cv2.putText(frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame
    
    def get_model_info(self):
        """Obtenir les informations du modèle actuel"""
        model_info = {
            'ArcFace': {'accuracy': '99.85%', 'architecture': 'ResNet-100', 'embedding': 512},
            'FaceNet': {'accuracy': '99.63%', 'architecture': 'Inception-ResNet v1', 'embedding': 128},
            'VGG-Face': {'accuracy': '98.97%', 'architecture': 'VGG-16', 'embedding': 2622},
            'OpenFace': {'accuracy': '95.00%', 'architecture': 'nn4.small2', 'embedding': 128},
            'DeepFace': {'accuracy': '90.00%', 'architecture': 'VGG-Face', 'embedding': 4096}
        }
        
        info = model_info.get(self.current_model, {'accuracy': 'N/A', 'architecture': 'N/A', 'embedding': 'N/A'})
        
        return {
            'model_name': self.current_model,
            'accuracy': info['accuracy'],
            'architecture': info['architecture'],
            'embedding_size': info['embedding'],
            'distance_metric': self.distance_metric,
            'confidence_threshold': self.confidence_threshold,
            'cache_timeout': self.cache_timeout,
            'min_face_size': self.min_face_size
        }
    
    def reload_settings(self):
        """Recharger les paramètres et réinitialiser le service"""
        print("Rechargement des paramètres...")
        self.load_settings()
        self.init_recognition_service()
        print(f"Service rechargé avec modèle: {self.current_model}")

# Fonction de compatibilité pour l'existant
def get_face_recognition_service(settings_file="final/config/settings.json"):
    """Obtenir le service de reconnaissance faciale dynamique"""
    return FaceRecognitionDynamic(settings_file)

if __name__ == "__main__":
    # Tester le service dynamique
    service = FaceRecognitionDynamic()
    print("=== INFOS SERVICE DYNAMIQUE ===")
    info = service.get_model_info()
    for key, value in info.items():
        print(f"{key}: {value}")
