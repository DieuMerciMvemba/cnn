"""
Interface principale Tkinter pour le système UCC
Pointage automatique avec reconnaissance faciale
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import os

# Import des services UCC
from database.database import DatabaseUCC
from services.face_recognition import FaceRecognitionUCC
from services.camera_service import CameraServiceUCC

class AttendanceAppUCC:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Pointage UCC - Reconnaissance Faciale")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Services
        self.database = DatabaseUCC()
        self.face_service = FaceRecognitionUCC()
        self.camera_service = CameraServiceUCC()
        
        # Variables
        self.is_running = False
        self.current_student = None
        self.attendance_count = 0
        
        # Initialiser l'interface
        self.setup_ui()
        self.load_students()
        
        # Démarrer la caméra
        self.start_camera()
        
        # Gérer la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configurer l'interface utilisateur"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Panneau de gauche - Caméra
        self.setup_camera_panel(main_frame)
        
        # Panneau de droite - Informations
        self.setup_info_panel(main_frame)
        
        # Barre de statut
        self.setup_status_bar()
    
    def setup_camera_panel(self, parent):
        """Configurer le panneau de caméra"""
        camera_frame = ttk.LabelFrame(parent, text="Caméra de Pointage", padding="10")
        camera_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Label pour l'affichage de la caméra
        self.camera_label = ttk.Label(camera_frame, text="Caméra en cours de démarrage...")
        self.camera_label.pack(pady=10)
        
        # Canvas pour la vidéo
        self.video_canvas = tk.Canvas(camera_frame, width=640, height=480, bg='black')
        self.video_canvas.pack(pady=10)
        
        # Boutons de contrôle
        button_frame = ttk.Frame(camera_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Démarrer Pointage", 
                                     command=self.toggle_attendance)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.capture_button = ttk.Button(button_frame, text="Capturer Photo", 
                                       command=self.capture_photo)
        self.capture_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Vider Cache", 
                                     command=self.clear_cache)
        self.clear_button.pack(side=tk.LEFT, padx=5)
    
    def setup_info_panel(self, parent):
        """Configurer le panneau d'informations"""
        info_frame = ttk.LabelFrame(parent, text="Informations de Pointage", padding="10")
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Informations étudiant
        student_frame = ttk.LabelFrame(info_frame, text="Étudiant Reconnu", padding="10")
        student_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.student_info = {
            'matricule': tk.StringVar(value="En attente..."),
            'nom': tk.StringVar(value=""),
            'faculte': tk.StringVar(value=""),
            'promotion': tk.StringVar(value=""),
            'statut': tk.StringVar(value=""),
            'confidence': tk.StringVar(value="")
        }
        
        # Affichage des informations
        info_labels = [
            ("Matricule:", 'matricule'),
            ("Nom Complet:", 'nom'),
            ("Faculté:", 'faculte'),
            ("Promotion:", 'promotion'),
            ("Statut:", 'statut'),
            ("Confiance:", 'confidence')
        ]
        
        for i, (label_text, var_key) in enumerate(info_labels):
            ttk.Label(student_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            label = ttk.Label(student_frame, textvariable=self.student_info[var_key], 
                           font=('Arial', 10, 'bold'))
            label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Statistiques
        stats_frame = ttk.LabelFrame(info_frame, text="Statistiques du Jour", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_vars = {
            'total_students': tk.StringVar(value="0"),
            'present_today': tk.StringVar(value="0"),
            'absent_today': tk.StringVar(value="0"),
            'attendance_rate': tk.StringVar(value="0%")
        }
        
        stats_labels = [
            ("Total Étudiants:", 'total_students'),
            ("Présents Aujourd'hui:", 'present_today'),
            ("Absents Aujourd'hui:", 'absent_today'),
            ("Taux de Présence:", 'attendance_rate')
        ]
        
        for i, (label_text, var_key) in enumerate(stats_labels):
            ttk.Label(stats_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            label = ttk.Label(stats_frame, textvariable=self.stats_vars[var_key], 
                           font=('Arial', 10, 'bold'))
            label.grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Historique récent
        history_frame = ttk.LabelFrame(info_frame, text="Historique Récent", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview pour l'historique
        columns = ('Heure', 'Matricule', 'Nom', 'Statut')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton rafraîchir
        ttk.Button(info_frame, text="Rafraîchir Statistiques", 
                  command=self.refresh_statistics).pack(pady=10)
    
    def setup_status_bar(self):
        """Configurer la barre de statut"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Prêt", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.fps_label = ttk.Label(status_frame, text="FPS: 0", relief=tk.SUNKEN)
        self.fps_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def load_students(self):
        """Charger les étudiants depuis la base de données"""
        students = self.database.get_students()
        
        students_db = {}
        for student in students:
            student_id = student['id']
            photo_path = student.get('photo_path')
            
            if photo_path and os.path.exists(photo_path):
                students_db[str(student_id)] = {
                    'name': f"{student['nom']} {student['postnom'] or ''} {student['prenom'] or ''}".strip(),
                    'faculte': student.get('faculte_nom', ''),
                    'promotion': student.get('promotion', ''),
                    'matricule': student.get('matricule', ''),
                    'photo_path': photo_path
                }
        
        self.face_service.load_student_database(students_db)
        self.update_status(f"{len(students_db)} étudiants chargés")
    
    def start_camera(self):
        """Démarrer la caméra"""
        if self.camera_service.start_capture():
            self.update_camera_display()
            self.update_status("Caméra démarrée")
        else:
            self.update_status("Erreur: Impossible de démarrer la caméra")
            messagebox.showerror("Erreur", "Impossible de démarrer la caméra")
    
    def update_camera_display(self):
        """Mettre à jour l'affichage de la caméra"""
        if not self.is_running:
            return
        
        # Obtenir la frame de la caméra
        frame = self.camera_service.get_frame()
        
        if frame is not None:
            # Traiter la frame avec reconnaissance faciale
            results = self.face_service.process_frame(frame)
            
            # Dessiner les résultats
            frame = self.face_service.draw_results(frame, results)
            
            # Ajouter les informations
            info_text = "Pointage UCC - Actif" if self.is_running else "Pointage UCC - Inactif"
            frame = self.camera_service.add_info_overlay(frame, info_text)
            
            # Convertir pour Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image = image.resize((640, 480), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image=image)
            
            # Mettre à jour le canvas
            self.video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.video_canvas.image = photo  # Garder une référence
            
            # Traiter les résultats de reconnaissance
            if results and self.is_running:
                self.process_recognition_results(results)
            
            # Mettre à jour FPS
            fps = self.camera_service.get_fps()
            self.fps_label.config(text=f"FPS: {fps:.1f}")
        
        # Planifier la prochaine mise à jour
        self.root.after(30, self.update_camera_display)
    
    def process_recognition_results(self, results):
        """Traiter les résultats de reconnaissance faciale"""
        for result in results:
            recognition = result['recognition']
            
            if recognition:
                # Étudiant reconnu
                self.current_student = recognition
                self.update_student_info(recognition)
                
                # Marquer la présence
                if self.mark_attendance(recognition):
                    self.add_to_history(recognition, "Présent")
                    self.attendance_count += 1
                    self.update_status(f"Présence marquée: {recognition['name']}")
            else:
                # Visage non reconnu
                self.current_student = None
                self.student_info['matricule'].set("Non reconnu")
                self.student_info['nom'].set("")
                self.student_info['faculte'].set("")
                self.student_info['promotion'].set("")
                self.student_info['statut'].set("")
                self.student_info['confidence'].set("")
    
    def update_student_info(self, student_data):
        """Mettre à jour les informations de l'étudiant"""
        self.student_info['matricule'].set(student_data.get('matricule', ''))
        self.student_info['nom'].set(student_data.get('name', ''))
        self.student_info['faculte'].set(student_data.get('faculte', ''))
        self.student_info['promotion'].set(student_data.get('promotion', ''))
        self.student_info['confidence'].set(f"{student_data.get('confidence', 0):.2f}")
        
        # Déterminer le statut
        current_time = datetime.now().time()
        if current_time.hour > 8:
            self.student_info['statut'].set("Retard")
        else:
            self.student_info['statut'].set("Présent")
    
    def mark_attendance(self, student_data):
        """Marquer la présence d'un étudiant"""
        # Ici, il faudrait retrouver l'ID de l'étudiant dans la base de données
        # Pour l'instant, nous utilisons une simulation
        try:
            # Simulation - à remplacer avec la vraie logique
            student_id = student_data.get('student_id', 1)
            
            # Marquer la présence
            success = self.database.mark_attendance(
                student_id, 
                'entree', 
                student_data.get('confidence', 0)
            )
            
            if success:
                self.refresh_statistics()
            
            return success
            
        except Exception as e:
            print(f"Erreur marquage présence: {e}")
            return False
    
    def add_to_history(self, student_data, status):
        """Ajouter à l'historique"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        self.history_tree.insert('', 0, values=(
            current_time,
            student_data.get('matricule', ''),
            student_data.get('name', ''),
            status
        ))
        
        # Limiter l'historique à 20 entrées
        children = self.history_tree.get_children()
        if len(children) > 20:
            self.history_tree.delete(children[-1])
    
    def toggle_attendance(self):
        """Démarrer/arrêter le pointage"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_button.config(text="Arrêter Pointage")
            self.update_status("Pointage actif")
        else:
            self.start_button.config(text="Démarrer Pointage")
            self.update_status("Pointage inactif")
    
    def capture_photo(self):
        """Capturer une photo"""
        photo_path = self.camera_service.save_frame()
        if photo_path:
            self.update_status(f"Photo sauvegardée: {photo_path}")
            messagebox.showinfo("Photo", f"Photo sauvegardée: {photo_path}")
        else:
            self.update_status("Erreur sauvegarde photo")
            messagebox.showerror("Erreur", "Impossible de sauvegarder la photo")
    
    def clear_cache(self):
        """Vider le cache de reconnaissance"""
        self.face_service.clear_cache()
        self.update_status("Cache vidé")
    
    def refresh_statistics(self):
        """Rafraîchir les statistiques"""
        stats = self.database.get_statistics()
        
        self.stats_vars['total_students'].set(str(stats['total_students']))
        self.stats_vars['present_today'].set(str(stats['present_today']))
        self.stats_vars['absent_today'].set(str(stats['absent_today']))
        self.stats_vars['attendance_rate'].set(f"{stats['attendance_rate']:.1f}%")
    
    def update_status(self, message):
        """Mettre à jour le statut"""
        self.status_label.config(text=message)
    
    def on_closing(self):
        """Gérer la fermeture de l'application"""
        self.is_running = False
        self.camera_service.stop_capture()
        self.root.destroy()

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = AttendanceAppUCC(root)
    root.mainloop()

if __name__ == "__main__":
    main()
