"""
Service de reconnaissance faciale pour UCC
Basé sur DeepFace avec optimisations pour performance
"""

import cv2
import os
import time
import numpy as np
from deepface import DeepFace
import threading
from datetime import datetime

class FaceRecognitionUCC:
    def __init__(self, model_path=".deepface/weights/vgg_face_weights.h5"):
        self.model_path = model_path
        self.students_db = {}
        self.face_cascade = None
        self.recognition_cache = {}
        self.cache_timeout = 5  # secondes
        self.last_recognition_time = {}
        self.min_face_size = (64, 64)
        
        # Initialiser le détecteur de visage
        self.init_face_detector()
        
        print("Service reconnaissance faciale UCC initialisé")
    
    def init_face_detector(self):
        """Initialiser le détecteur de visage Haar Cascade"""
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
    
    def load_student_database(self, students_data):
        """Charger la base de données des étudiants"""
        self.students_db = students_data
        print(f"Base chargée: {len(students_data)} étudiants")
    
    def detect_faces(self, frame):
        """Détecter les visages dans une image"""
        if self.face_cascade is None:
            return []
        
        try:
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Détecter les visages
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
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
        return face_roi
    
    def recognize_face(self, face_image, student_id_hint=None):
        """Reconnaître un visage avec DeepFace"""
        current_time = time.time()
        
        # Vérifier le cache
        cache_key = f"{id(face_image)}_{student_id_hint}"
        if (cache_key in self.recognition_cache and 
            current_time - self.recognition_cache[cache_key]['time'] < self.cache_timeout):
            return self.recognition_cache[cache_key]['result']
        
        try:
            # Limiter le nombre de comparaisons pour la performance
            max_comparisons = min(10, len(self.students_db))
            students_to_compare = list(self.students_db.items())[:max_comparisons]
            
            best_match = None
            best_score = 0
            
            for student_id, student_info in students_to_compare:
                # Skip si hint fourni et différent
                if student_id_hint and student_id != student_id_hint:
                    continue
                
                photo_path = student_info.get('photo_path')
                if not photo_path or not os.path.exists(photo_path):
                    continue
                
                try:
                    # Comparaison avec DeepFace
                    result = DeepFace.verify(
                        face_image,
                        photo_path,
                        model_name='VGG-Face',
                        enforce_detection=False,
                        detector_backend='skip'
                    )
                    
                    if result['verified']:
                        distance = result.get('distance', 0)
                        score = 1 - distance  # Convertir distance en score
                        
                        if score > best_score:
                            best_score = score
                            best_match = {
                                'student_id': student_id,
                                'name': student_info.get('name', ''),
                                'faculte': student_info.get('faculte', ''),
                                'promotion': student_info.get('promotion', ''),
                                'matricule': student_info.get('matricule', ''),
                                'confidence': score
                            }
                
                except Exception as e:
                    # Ignorer les erreurs individuelles
                    continue
            
            # Mettre en cache le résultat
            result = best_match if best_match and best_score > 0.6 else None
            self.recognition_cache[cache_key] = {
                'result': result,
                'time': current_time
            }
            
            return result
            
        except Exception as e:
            print(f"Erreur reconnaissance: {e}")
            return None
    
    def process_frame(self, frame):
        """Traiter une frame complète: détection + reconnaissance"""
        results = []
        
        # Détecter les visages
        faces = self.detect_faces(frame)
        
        for face_coords in faces:
            # Extraire le visage
            face_roi = self.extract_face_roi(frame, face_coords)
            
            if face_roi is None:
                continue
            
            # Reconnaître le visage
            recognition_result = self.recognize_face(face_roi)
            
            result = {
                'face_coords': face_coords,
                'recognition': recognition_result,
                'timestamp': datetime.now()
            }
            
            results.append(result)
        
        return results
    
    def is_real_face(self, face_image):
        """Détection basique anti-spoofing (photo vs visage réel)"""
        try:
            # Analyse de la netteté
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Seuil de netteté
            if laplacian_var < 100:
                return False, "Image trop floue"
            
            # Vérifier les dimensions minimales
            h, w = face_image.shape[:2]
            if h < 64 or w < 64:
                return False, "Visage trop petit"
            
            # Vérifier le ratio (pas de visage trop étiré)
            ratio = w / h
            if ratio < 0.7 or ratio > 1.4:
                return False, "Ratio visage incorrect"
            
            return True, "Visage valide"
            
        except Exception as e:
            print(f"Erreur anti-spoofing: {e}")
            return True, "Validation par défaut"
    
    def draw_results(self, frame, results):
        """Dessiner les résultats sur la frame"""
        for result in results:
            x, y, w, h = result['face_coords']
            recognition = result['recognition']
            
            if recognition:
                # Visage reconnu - rectangle vert
                color = (0, 255, 0)
                label = f"{recognition['name']}"
                confidence = recognition['confidence']
                
                # Ajouter la faculté et promotion
                if recognition.get('faculte') and recognition.get('promotion'):
                    label += f" - {recognition['faculte']} {recognition['promotion']}"
                
                # Ajouter la confiance
                label += f" ({confidence:.2f})"
                
            else:
                # Visage non reconnu - rectangle rouge
                color = (0, 0, 255)
                label = "Non reconnu"
            
            # Dessiner le rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Dessiner le label
            label_y = y - 10 if y > 30 else y + h + 30
            cv2.putText(frame, label, (x, label_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
    
    def clear_cache(self):
        """Vider le cache de reconnaissance"""
        self.recognition_cache.clear()
        self.last_recognition_time.clear()
        print("Cache de reconnaissance vidé")
    
    def get_performance_stats(self):
        """Obtenir les statistiques de performance"""
        return {
            'cache_size': len(self.recognition_cache),
            'students_loaded': len(self.students_db),
            'detector_loaded': self.face_cascade is not None
        }

# Test du service
if __name__ == "__main__":
    # Données test
    test_students = {
        'student1': {
            'name': 'Jean Dupont',
            'faculte': 'Sciences Informatiques',
            'promotion': 'LICENCE 2',
            'matricule': 'UCC-2024-2-0001',
            'photo_path': 'Dataset/Dieudonne.jpg'  # Utiliser une image existante
        }
    }
    
    # Initialiser le service
    face_service = FaceRecognitionUCC()
    face_service.load_student_database(test_students)
    
    print("Service reconnaissance faciale UCC prêt!")
    print(face_service.get_performance_stats())
