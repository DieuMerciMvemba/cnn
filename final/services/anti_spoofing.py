"""
Service Anti-Spoofing - Système UCC
Détection de faux visages (photos, masques, deepfakes)
"""

import cv2
import numpy as np
import time
from deepface import DeepFace
from retinaface import RetinaFace
import os

class AntiSpoofingService:
    def __init__(self):
        self.face_detector = RetinaFace()
        self.blink_detector = None
        self.liveness_threshold = 0.5
        self.blink_threshold = 3  # clignements requis
        self.blink_count = 0
        self.last_blink_time = 0
        self.face_history = []
        self.max_history = 10
        
        print("Service Anti-Spoofing initialisé")
    
    def detect_liveness(self, face_image, face_coords=None):
        """Détection de liveness (visage vivant)"""
        try:
            # 1. Détection de clignement des yeux
            blink_result = self.detect_blink(face_image)
            
            # 2. Analyse de texture (détection photo)
            texture_result = self.analyze_texture(face_image)
            
            # 3. Détection de mouvement micro
            movement_result = self.detect_micro_movement(face_image)
            
            # 4. Analyse de profondeur (si disponible)
            depth_result = self.analyze_depth(face_image)
            
            # Score combiné
            liveness_score = (
                blink_result * 0.4 +      # Clignement le plus important
                texture_result * 0.3 +    # Texture
                movement_result * 0.2 +    # Mouvement
                depth_result * 0.1        # Profondeur
            )
            
            is_live = liveness_score > self.liveness_threshold
            
            return {
                'is_live': is_live,
                'score': liveness_score,
                'blink_detected': blink_result > 0.3,
                'texture_score': texture_result,
                'movement_score': movement_result,
                'depth_score': depth_result,
                'confidence': liveness_score
            }
            
        except Exception as e:
            print(f"Erreur liveness detection: {e}")
            return {'is_live': False, 'score': 0, 'error': str(e)}
    
    def detect_blink(self, face_image):
        """Détection de clignement des yeux"""
        try:
            # Utiliser RetinaFace pour détecter les points faciaux
            faces = RetinaFace.extract_faces(face_image, align=True)
            
            if not faces:
                return 0.0
            
            face = faces[0]
            if len(face) < 3:
                return 0.0
            
            # Extraire la région des yeux
            eye_region = face[0]  # visage aligné
            
            # Convertir en niveaux de gris pour l'analyse des yeux
            gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
            
            # Détecter les yeux avec OpenCV (méthode simple)
            eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(eyes) >= 2:
                # Analyser le rapport aspect des yeux
                blink_score = 0.0
                for (ex, ey, ew, eh) in eyes[:2]:
                    aspect_ratio = ew / eh if eh > 0 else 0
                    
                    # Yeux fermés = aspect ratio plus faible
                    if aspect_ratio < 2.0:  # Seuil pour yeux fermés
                        blink_score += 0.5
                
                blink_score = min(blink_score, 1.0)
                
                # Comptabiliser les clignements
                current_time = time.time()
                if blink_score > 0.5 and current_time - self.last_blink_time > 0.3:
                    self.blink_count += 1
                    self.last_blink_time = current_time
                
                return blink_score
            
            return 0.0
            
        except Exception as e:
            print(f"Erreur blink detection: {e}")
            return 0.0
    
    def analyze_texture(self, face_image):
        """Analyser la texture pour détecter les photos"""
        try:
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Calculer le gradient pour détecter les textures
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Analyser les patterns de texture
            # Les vrais visages ont plus de variation de texture
            texture_variance = np.var(gradient_magnitude)
            
            # Les photos imprimées ont souvent des patterns réguliers
            # Détecter les patterns périodiques avec FFT
            fft = np.fft.fft2(gray)
            fft_shift = np.fft.fftshift(fft)
            
            # Analyser les hautes fréquences (détails fins)
            h, w = gray.shape
            center_h, center_w = h // 2, w // 2
            
            # Masque pour les hautes fréquences
            mask = np.zeros((h, w), np.uint8)
            mask[center_h-30:center_h+30, center_w-30:center_w+30] = 0
            mask = 1 - mask
            
            high_freq_energy = np.sum(np.abs(fft_shift) * mask)
            total_energy = np.sum(np.abs(fft_shift))
            
            high_freq_ratio = high_freq_energy / total_energy if total_energy > 0 else 0
            
            # Score de texture (0 = photo, 1 = vrai visage)
            texture_score = min(texture_variance / 1000 + high_freq_ratio, 1.0)
            
            return texture_score
            
        except Exception as e:
            print(f"Erreur texture analysis: {e}")
            return 0.5  # Neutre en cas d'erreur
    
    def detect_micro_movement(self, face_image):
        """Détecter les micro-mouvements (respiration, tremblements)"""
        try:
            # Ajouter l'image actuelle à l'historique
            current_time = time.time()
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            self.face_history.append({
                'image': gray,
                'time': current_time
            })
            
            # Garder seulement les N dernières images
            if len(self.face_history) > self.max_history:
                self.face_history.pop(0)
            
            if len(self.face_history) < 3:
                return 0.5  # Pas assez d'historique
            
            # Analyser les mouvements entre les frames
            movement_scores = []
            
            for i in range(1, len(self.face_history)):
                prev_gray = self.face_history[i-1]['image']
                curr_gray = self.face_history[i]['image']
                
                # Calculer le flux optique (mouvement)
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray, 
                    np.array([[100, 100]], dtype=np.float32), 
                    None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    movement_magnitude = np.sqrt(flow[0,0]**2 + flow[0,1]**2)
                    movement_scores.append(movement_magnitude)
            
            if movement_scores:
                avg_movement = np.mean(movement_scores)
                # Les vrais visages ont des micro-mouvements (respiration)
                # Les photos sont statiques
                movement_score = min(avg_movement / 5.0, 1.0)
                return movement_score
            
            return 0.5
            
        except Exception as e:
            print(f"Erreur micro-movement detection: {e}")
            return 0.5
    
    def analyze_depth(self, face_image):
        """Analyser la profondeur (détection 2D vs 3D)"""
        try:
            # Utiliser le flou de mise au point
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Calculer le Laplacian variance (mesure de flou)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Les vrais visages 3D ont plus de variation de profondeur
            # Les photos 2D sont souvent plus plates
            depth_score = min(laplacian_var / 500, 1.0)
            
            return depth_score
            
        except Exception as e:
            print(f"Erreur depth analysis: {e}")
            return 0.5
    
    def detect_spoofing_type(self, face_image):
        """Détecter le type de spoofing"""
        try:
            liveness_result = self.detect_liveness(face_image)
            
            if not liveness_result.get('is_live', False):
                # Analyser le type de spoofing
                texture_score = liveness_result.get('texture_score', 0)
                movement_score = liveness_result.get('movement_score', 0)
                depth_score = liveness_result.get('depth_score', 0)
                
                if texture_score < 0.3 and movement_score < 0.2:
                    return {
                        'is_spoof': True,
                        'type': 'Photo imprimée',
                        'confidence': 0.8
                    }
                elif texture_score < 0.4 and movement_score < 0.3:
                    return {
                        'is_spoof': True,
                        'type': 'Photo sur écran',
                        'confidence': 0.7
                    }
                elif depth_score < 0.3:
                    return {
                        'is_spoof': True,
                        'type': 'Masque 2D',
                        'confidence': 0.6
                    }
                else:
                    return {
                        'is_spoof': True,
                        'type': 'Inconnu',
                        'confidence': 0.5
                    }
            
            return {
                'is_spoof': False,
                'type': 'Visage authentique',
                'confidence': liveness_result.get('score', 0)
            }
            
        except Exception as e:
            print(f"Erreur spoofing detection: {e}")
            return {'is_spoof': False, 'type': 'Erreur', 'confidence': 0}
    
    def reset_blink_counter(self):
        """Réinitialiser le compteur de clignements"""
        self.blink_count = 0
        self.face_history = []
    
    def get_blink_status(self):
        """Obtenir le statut de clignement"""
        return {
            'blink_count': self.blink_count,
            'required': self.blink_threshold,
            'completed': self.blink_count >= self.blink_threshold
        }

# Test du service anti-spoofing
if __name__ == "__main__":
    anti_spoof = AntiSpoofingService()
    print("Service Anti-Spoofing prêt")
    print(f"Clignements requis: {anti_spoof.blink_threshold}")
    print(f"Seuil liveness: {anti_spoof.liveness_threshold}")
