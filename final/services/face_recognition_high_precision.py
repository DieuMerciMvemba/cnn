"""
Service de reconnaissance faciale HAUTE PRÉCISION - Système UCC
Optimisé pour précision maximale avec validation multiple
"""

import cv2
import os
import time
import numpy as np
from deepface import DeepFace
import threading
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class HighPrecisionFaceRecognition:
    def __init__(self, model_name='VGG-Face', settings_file="final/config/settings.json"):
        self.model_name = model_name
        self.settings_file = settings_file
        self.students_db = {}
        self.face_cascade = None
        self.recognition_cache = {}
        self.cache_timeout = 3  # Réduit pour précision
        self.last_recognition_time = {}
        self.min_face_size = (80, 80)  # Augmenté pour meilleure qualité
        
        # Paramètres de haute précision
        self.confidence_thresholds = {
            'VGG-Face': 0.65,      # Augmenté de 0.6
            'Facenet': 0.70,       # Augmenté de 0.65  
            'ArcFace': 0.75,       # Augmenté de 0.7
            'OpenFace': 0.60,      # Augmenté de 0.55
            'DeepFace': 0.55       # Augmenté de 0.5
        }
        
        self.distance_metrics = {
            'VGG-Face': 'cosine',
            'Facenet': 'euclidean_l2',
            'ArcFace': 'cosine',
            'OpenFace': 'cosine',
            'DeepFace': 'cosine'
        }
        
        # Initialiser
        self.init_face_detector()
        self.load_settings()
        
        print(f"Service reconnaissance HAUTE PRÉCISION initialisé: {model_name}")
    
    def load_settings(self):
        """Charger les paramètres depuis le fichier"""
        try:
            if os.path.exists(self.settings_file):
                import json
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                recognition = settings.get('recognition', {})
                model_from_settings = recognition.get('model', 'VGG-Face')
                
                # Mettre à jour le modèle si différent
                if model_from_settings in self.confidence_thresholds:
                    self.model_name = model_from_settings
                
        except Exception as e:
            print(f"Erreur chargement paramètres: {e}")
    
    def init_face_detector(self):
        """Initialiser le détecteur de visage Haar Cascade optimisé"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if self.face_cascade.empty():
                raise Exception("Impossible de charger Haar Cascade")
            print("Détecteur de visage optimisé initialisé")
        except Exception as e:
            print(f"Erreur initialisation détecteur: {e}")
            self.face_cascade = None
    
    def load_student_database(self, students_data):
        """Charger la base de données des étudiants"""
        self.students_db = students_data
        print(f"Base chargée: {len(students_db)} étudiants pour {self.model_name}")
    
    def detect_faces(self, frame) -> List[Tuple[int, int, int, int]]:
        """Détecter les visages avec paramètres optimisés"""
        if self.face_cascade is None:
            return []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Paramètres optimisés pour précision
            scale_factor = 1.05  # Plus précis
            min_neighbors = 6    # Plus strict
            
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=self.min_face_size,
                maxSize=(300, 300)  # Limiter taille
            )
            
            return faces
        except Exception as e:
            print(f"Erreur détection visage: {e}")
            return []
    
    def extract_face_roi(self, frame, face_coords) -> Optional[np.ndarray]:
        """Extraire et prétraiter le visage pour haute précision"""
        x, y, w, h = face_coords
        
        # S'assurer que les coordonnées sont valides
        x = max(0, x)
        y = max(0, y)
        w = min(w, frame.shape[1] - x)
        h = min(h, frame.shape[0] - y)
        
        if w < self.min_face_size[0] or h < self.min_face_size[1]:
            return None
        
        face_roi = frame[y:y+h, x:x+w]
        
        # Prétraitement selon le modèle
        if self.model_name == 'ArcFace':
            face_roi = cv2.resize(face_roi, (112, 112))
        elif self.model_name == 'Facenet':
            face_roi = cv2.resize(face_roi, (160, 160))
        else:
            face_roi = cv2.resize(face_roi, (224, 224))
        
        # Normalisation
        face_roi = cv2.normalize(face_roi, None, 0, 255, cv2.NORM_MINMAX)
        
        return face_roi
    
    def recognize_face(self, face_image, student_id_hint=None) -> Optional[Dict]:
        """Reconnaître un visage avec haute précision"""
        current_time = time.time()
        
        # Cache plus court pour précision
        cache_key = f"{id(face_image)}_{student_id_hint}_{self.model_name}"
        if (cache_key in self.recognition_cache and 
            current_time - self.recognition_cache[cache_key]['time'] < self.cache_timeout):
            return self.recognition_cache[cache_key]['result']
        
        try:
            # Augmenter le nombre de comparaisons pour précision
            max_comparisons = min(50, len(self.students_db))  # Augmenté de 10 à 50
            students_to_compare = list(self.students_db.items())[:max_comparisons]
            
            # Stocker tous les scores pour validation
            all_scores = []
            matches = []
            
            distance_metric = self.distance_metrics.get(self.model_name, 'cosine')
            threshold = self.confidence_thresholds.get(self.model_name, 0.6)
            
            for student_id, student_info in students_to_compare:
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
                        model_name=self.model_name,
                        detector_backend='skip',
                        distance_metric=distance_metric,
                        enforce_detection=False
                    )
                    
                    if result['verified']:
                        distance = result.get('distance', 0)
                        
                        # Conversion précise selon la métrique
                        if distance_metric == 'cosine':
                            score = 1 - distance
                        elif distance_metric == 'euclidean_l2':
                            score = 1 / (1 + distance)
                        else:
                            score = max(0, 1 - distance)
                        
                        # Seuils stricts
                        if score > threshold:
                            all_scores.append(score)
                            matches.append({
                                'student_id': student_id,
                                'name': student_info.get('name', ''),
                                'faculte': student_info.get('faculte', ''),
                                'promotion': student_info.get('promotion', ''),
                                'matricule': student_info.get('matricule', ''),
                                'confidence': score,
                                'distance': distance,
                                'model': self.model_name
                            })
                
                except Exception as e:
                    continue
            
            # Validation multi-critères
            if not matches:
                return None
            
            # Trier par score de confiance
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Validation finale
            best_match = matches[0]
            
            # Critère 1: Score minimum
            if best_match['confidence'] < threshold:
                return None
            
            # Critère 2: Différence significative avec le 2ème (si existant)
            if len(matches) > 1:
                second_best = matches[1]
                score_diff = best_match['confidence'] - second_best['confidence']
                
                # Doit avoir au moins 10% de différence
                if score_diff < 0.1:
                    # Ambiguïté détectée
                    print(f"Ambiguïté: scores trop proches {best_match['confidence']:.3f} vs {second_best['confidence']:.3f}")
                    return None
            
            # Critère 3: Cohérence des scores (si plusieurs bons scores)
            if len(all_scores) > 2:
                mean_score = np.mean(all_scores)
                std_score = np.std(all_scores)
                
                # Le meilleur score doit être significativement au-dessus de la moyenne
                if best_match['confidence'] < mean_score + std_score:
                    print(f"Score pas assez significatif: {best_match['confidence']:.3f} vs moyenne {mean_score:.3f}")
                    return None
            
            # Ajouter des métadonnées de précision
            best_match.update({
                'total_comparisons': len(students_to_compare),
                'valid_matches': len(matches),
                'avg_score': np.mean(all_scores) if all_scores else 0,
                'score_std': np.std(all_scores) if len(all_scores) > 1 else 0,
                'precision_level': 'HIGH' if best_match['confidence'] > 0.8 else 'MEDIUM'
            })
            
            # Mettre en cache
            self.recognition_cache[cache_key] = {
                'result': best_match,
                'time': current_time
            }
            
            return best_match
            
        except Exception as e:
            print(f"Erreur reconnaissance {self.model_name}: {e}")
            return None
    
    def process_frame(self, frame) -> List[Dict]:
        """Traiter une frame complète avec haute précision"""
        results = []
        
        faces = self.detect_faces(frame)
        
        for (x, y, w, h) in faces:
            face_roi = self.extract_face_roi(frame, (x, y, w, h))
            
            if face_roi is None:
                continue
            
            recognition = self.recognize_face(face_roi)
            
            results.append({
                'bbox': (x, y, w, h),
                'recognition': recognition,
                'confidence': recognition['confidence'] if recognition else 0
            })
        
        return results
    
    def draw_results(self, frame, results):
        """Dessiner les résultats avec informations de précision"""
        for result in results:
            x, y, w, h = result['bbox']
            recognition = result['recognition']
            
            if recognition:
                # Couleur selon niveau de précision
                if recognition['confidence'] > 0.85:
                    color = (0, 255, 0)  # Vert - Très précis
                elif recognition['confidence'] > 0.7:
                    color = (0, 200, 0)  # Vert clair - Précis
                else:
                    color = (255, 255, 0)  # Jaune - Moyen
                
                label = (f"{recognition['name']} [{recognition['model']}] "
                        f"({recognition['confidence']:.2f}) "
                        f"🎯{recognition['precision_level']}")
            else:
                color = (0, 0, 255)  # Rouge - Non reconnu
                label = f"Non reconnu [{self.model_name}]"
            
            # Dessiner le rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Dessiner le label
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x, y - label_size[1] - 10), 
                         (x + label_size[0], y), color, -1)
            cv2.putText(frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame
    
    def get_precision_stats(self) -> Dict:
        """Obtenir les statistiques de précision"""
        threshold = self.confidence_thresholds.get(self.model_name, 0.6)
        distance_metric = self.distance_metrics.get(self.model_name, 'cosine')
        
        return {
            'model': self.model_name,
            'confidence_threshold': threshold,
            'distance_metric': distance_metric,
            'min_face_size': self.min_face_size,
            'cache_timeout': self.cache_timeout,
            'max_comparisons': min(50, len(self.students_db)),
            'precision_level': 'HIGH' if threshold >= 0.7 else 'MEDIUM'
        }

# Test du service de haute précision
if __name__ == "__main__":
    service = HighPrecisionFaceRecognition('ArcFace')
    print("=== SERVICE HAUTE PRÉCISION ===")
    stats = service.get_precision_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
