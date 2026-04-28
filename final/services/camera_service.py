"""
Service de gestion de caméra pour UCC
Capture vidéo avec threading pour performance
"""

import cv2
import threading
import time
from datetime import datetime
import os

class CameraServiceUCC:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # Configuration caméra
        self.width = 640
        self.height = 480
        self.fps_target = 30
        
    def initialize_camera(self):
        """Initialiser la caméra"""
        try:
            cap = None
            backends_to_try = [None]

            try:
                if os.name == 'nt' and hasattr(cv2, 'CAP_DSHOW'):
                    backends_to_try = [cv2.CAP_DSHOW, None]
            except Exception:
                backends_to_try = [None]

            for backend in backends_to_try:
                try:
                    if backend is None:
                        cap = cv2.VideoCapture(self.camera_id)
                    else:
                        cap = cv2.VideoCapture(self.camera_id, backend)

                    if cap is not None:
                        try:
                            if hasattr(cv2, 'CAP_PROP_OPEN_TIMEOUT_MSEC'):
                                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 2000)
                            if hasattr(cv2, 'CAP_PROP_READ_TIMEOUT_MSEC'):
                                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 2000)
                        except Exception:
                            pass

                    if cap is not None and cap.isOpened():
                        break
                except Exception:
                    cap = None

            self.cap = cap
            
            if not self.cap.isOpened():
                raise Exception(f"Impossible d'ouvrir la caméra {self.camera_id}")
            
            # Configurer la résolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
            
            # Vérifier la configuration
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"Caméra initialisée: {actual_width}x{actual_height} @ {actual_fps:.1f} FPS")
            
            return True
            
        except Exception as e:
            print(f"Erreur initialisation caméra: {e}")
            return False
    
    def start_capture(self):
        """Démarrer la capture en continu"""
        if self.is_running:
            return False
        
        if not self.initialize_camera():
            return False
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        print("Capture vidéo démarrée")
        return True
    
    def stop_capture(self):
        """Arrêter la capture"""
        self.is_running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        print("Capture vidéo arrêtée")
    
    def _capture_loop(self):
        """Boucle de capture dans un thread séparé"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if ret:
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                    
                    # Calculer FPS
                    self.frame_count += 1
                    current_time = time.time()
                    
                    if current_time - self.last_fps_time >= 1.0:
                        self.fps = self.frame_count / (current_time - self.last_fps_time)
                        self.frame_count = 0
                        self.last_fps_time = current_time
                
                else:
                    print("Erreur lecture frame")
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Erreur capture loop: {e}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Obtenir la frame actuelle"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
    
    def get_fps(self):
        """Obtenir le FPS actuel"""
        return self.fps
    
    def save_frame(self, filename=None, directory="captures"):
        """Sauvegarder la frame actuelle"""
        frame = self.get_frame()
        if frame is None:
            return None
        
        # Créer le répertoire si nécessaire
        os.makedirs(directory, exist_ok=True)
        
        # Générer le nom de fichier
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
        
        filepath = os.path.join(directory, filename)
        
        # Sauvegarder l'image
        success = cv2.imwrite(filepath, frame)
        
        if success:
            return filepath
        else:
            print(f"Erreur sauvegarde image: {filepath}")
            return None
    
    def add_info_overlay(self, frame, info_text):
        """Ajouter des informations sur la frame"""
        h, w = frame.shape[:2]
        
        # Rectangle de fond pour le texte
        cv2.rectangle(frame, (10, 10), (w-10, 80), (0, 0, 0), -1)
        
        # Texte principal
        cv2.putText(frame, info_text, (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # FPS
        fps_text = f"FPS: {self.fps:.1f}"
        cv2.putText(frame, fps_text, (20, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Timestamp
        timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp_text, (w-200, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def list_available_cameras(self):
        """Lister les caméras disponibles"""
        available_cameras = []
        
        for i in range(5):  # Tester les 5 premières caméras
            cap = None
            try:
                if os.name == 'nt' and hasattr(cv2, 'CAP_DSHOW'):
                    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(i)
            except Exception:
                cap = None
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        
        return available_cameras
    
    def get_camera_info(self):
        """Obtenir les informations de la caméra"""
        if self.cap is None:
            return None
        
        info = {
            'camera_id': self.camera_id,
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'backend': self.cap.getBackendName(),
            'current_fps': self.fps,
            'is_running': self.is_running
        }
        
        return info
    
    def resize_frame(self, frame, width=None, height=None):
        """Redimensionner une frame"""
        if frame is None:
            return None
        
        if width is None and height is None:
            return frame
        
        h, w = frame.shape[:2]
        
        if width is None:
            ratio = height / h
            width = int(w * ratio)
        elif height is None:
            ratio = width / w
            height = int(h * ratio)
        
        return cv2.resize(frame, (width, height))
    
    def enhance_frame(self, frame):
        """Améliorer la qualité de la frame"""
        if frame is None:
            return None
        
        # Légère augmentation de contraste
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Appliquer CLAHE au canal L
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Recombiner
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def __del__(self):
        """Destructeur"""
        self.stop_capture()

# Test du service
if __name__ == "__main__":
    camera = CameraServiceUCC()
    
    print("Caméras disponibles:", camera.list_available_cameras())
    
    if camera.start_capture():
        print("Camera démarrée, test de 5 secondes...")
        time.sleep(5)
        
        # Test sauvegarde
        saved_path = camera.save_frame()
        if saved_path:
            print(f"Image sauvegardée: {saved_path}")
        
        # Test informations
        info = camera.get_camera_info()
        print("Info caméra:", info)
        
        camera.stop_capture()
    else:
        print("Impossible de démarrer la caméra")
