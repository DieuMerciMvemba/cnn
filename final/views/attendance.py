"""
Module Pointage - Système UCC
Interface de reconnaissance faciale avec caméra
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import os

# Import des services
from services.camera_service import CameraServiceUCC
from services.face_recognition_dynamic import FaceRecognitionDynamic

class AttendanceScreen:
    def __init__(self, root, user_data, database):
        self.root = root
        self.user_data = user_data
        self.database = database
        
        # Services
        self.face_service = FaceRecognitionDynamic()
        self.camera_service = CameraServiceUCC()
        
        # Variables
        self.is_running = False
        self.current_student = None
        self.attendance_count = 0
        
        # Configuration fenêtre
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les étudiants
        self.load_students()
        
        # Démarrer la caméra
        self.start_camera()
        
        # Gérer la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        self.create_header()
        
        # Contenu principal
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panneau gauche - Caméra
        self.create_camera_panel(main_container)
        
        # Panneau droit - Informations
        self.create_info_panel(main_container)
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.root, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(header, text="📸 POINTAGE - RECONNAISSANCE FACIALE", 
                              font=('Arial', 18, 'bold'), bg='#003366', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Boutons de contrôle
        controls_frame = tk.Frame(header, bg='#003366')
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        control_frame = tk.Frame(controls_frame, bg='white', relief=tk.RAISED, borderwidth=1)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton démarrer/arrêter
        self.start_btn = tk.Button(control_frame, text="▶️ DÉMARRER POINTAGE", 
                                  command=self.toggle_attendance, bg='#28a745', fg='white',
                                  font=('Arial', 12, 'bold'), relief=tk.FLAT, cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bouton recharger paramètres
        reload_btn = tk.Button(control_frame, text="🔄 Recharger Paramètres", 
                              command=self.reload_settings, bg='#007bff', fg='white',
                              font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        reload_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        capture_btn = tk.Button(controls_frame, text="📸 CAPTURER", 
                                command=self.capture_photo,
                                bg='#17a2b8', fg='white', font=('Arial', 10),
                                relief=tk.FLAT, cursor='hand2')
        capture_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(controls_frame, text="🗑️ VIDER", 
                              command=self.clear_students,
                              bg='#6c757d', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def create_camera_panel(self, parent):
        """Créer le panneau de caméra"""
        camera_frame = tk.LabelFrame(parent, text="CAMÉRA DE POINTAGE", 
                                    font=('Arial', 14, 'bold'), bg='white')
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Canvas pour la vidéo
        self.video_canvas = tk.Canvas(camera_frame, width=640, height=480, 
                                     bg='black', highlightthickness=0)
        self.video_canvas.pack(pady=20, padx=20)
        
        # Informations caméra
        info_frame = tk.Frame(camera_frame, bg='white')
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.fps_label = tk.Label(info_frame, text="FPS: 0", 
                                  font=('Arial', 10), bg='white', fg='#666')
        self.fps_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(info_frame, text="🔴 Caméra inactive", 
                                     font=('Arial', 10, 'bold'), bg='white', fg='#dc3545')
        self.status_label.pack(side=tk.RIGHT)
        
        # Message de feedback
        self.feedback_label = tk.Label(camera_frame, text="Placez votre visage devant la caméra", 
                                     font=('Arial', 12), bg='white', fg='#666')
        self.feedback_label.pack(pady=(0, 20))
    
    def create_info_panel(self, parent):
        """Créer le panneau d'informations"""
        info_frame = tk.LabelFrame(parent, text="INFORMATIONS DE POINTAGE", 
                                   font=('Arial', 14, 'bold'), bg='white')
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Informations étudiant
        student_frame = tk.LabelFrame(info_frame, text="ÉTUDIANT RECONNU", 
                                     font=('Arial', 12, 'bold'), bg='white')
        student_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Variables étudiant
        self.student_vars = {
            'matricule': tk.StringVar(value="En attente..."),
            'nom': tk.StringVar(value=""),
            'faculte': tk.StringVar(value=""),
            'promotion': tk.StringVar(value=""),
            'confidence': tk.StringVar(value=""),
            'statut': tk.StringVar(value="")
        }
        
        # Affichage des informations
        info_fields = [
            ("Matricule:", 'matricule'),
            ("Nom Complet:", 'nom'),
            ("Faculté:", 'faculte'),
            ("Promotion:", 'promotion'),
            ("Confiance:", 'confidence'),
            ("Statut:", 'statut')
        ]
        
        for i, (label_text, var_key) in enumerate(info_fields):
            tk.Label(student_frame, text=label_text, font=('Arial', 11), 
                    bg='white', anchor='w').grid(row=i, column=0, sticky='w', 
                                                 pady=5, padx=(10, 0))
            
            value_label = tk.Label(student_frame, textvariable=self.student_vars[var_key], 
                                  font=('Arial', 11, 'bold'), bg='white', anchor='w')
            value_label.grid(row=i, column=1, sticky='w', pady=5, padx=(20, 10))
        
        # Statistiques du jour
        stats_frame = tk.LabelFrame(info_frame, text="STATISTIQUES DU JOUR", 
                                    font=('Arial', 12, 'bold'), bg='white')
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Variables statistiques
        self.stats_vars = {
            'total_students': tk.StringVar(value="0"),
            'present_today': tk.StringVar(value="0"),
            'absent_today': tk.StringVar(value="0"),
            'attendance_rate': tk.StringVar(value="0%")
        }
        
        stats_fields = [
            ("Total Étudiants:", 'total_students'),
            ("Présents Aujourd'hui:", 'present_today'),
            ("Absents Aujourd'hui:", 'absent_today'),
            ("Taux de Présence:", 'attendance_rate')
        ]
        
        for i, (label_text, var_key) in enumerate(stats_fields):
            tk.Label(stats_frame, text=label_text, font=('Arial', 11), 
                    bg='white', anchor='w').grid(row=i, column=0, sticky='w', 
                                                pady=5, padx=(10, 0))
            
            value_label = tk.Label(stats_frame, textvariable=self.stats_vars[var_key], 
                                  font=('Arial', 11, 'bold'), bg='white', anchor='w')
            value_label.grid(row=i, column=1, sticky='w', pady=5, padx=(20, 10))
        
        # Historique récent
        history_frame = tk.LabelFrame(info_frame, text="HISTORIQUE RÉCENT", 
                                     font=('Arial', 12, 'bold'), bg='white')
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview pour l'historique
        columns = ('Heure', 'Matricule', 'Nom', 'Statut')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                         show='headings', height=10)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        # Bouton rafraîchir
        refresh_btn = tk.Button(info_frame, text="🔄 Rafraîchir", 
                               command=self.refresh_statistics,
                               bg='#007bff', fg='white', font=('Arial', 10),
                               relief=tk.FLAT, cursor='hand2')
        refresh_btn.pack(pady=20)
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.root, bg='#f0f0f0', height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Compteur
        counter_frame = tk.Frame(footer, bg='#f0f0f0')
        counter_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.counter_label = tk.Label(counter_frame, text="Pointages aujourd'hui: 0", 
                                     font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#003366')
        self.counter_label.pack()
        
        # Bouton fermer
        close_btn = tk.Button(footer, text="Fermer", command=self.on_closing,
                              bg='#6c757d', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def load_students(self):
        """Charger les étudiants depuis la base de données"""
        try:
            students = self.database.get_students()
            
            students_db = {}
            for student in students:
                try:
                    student_id = student['id']
                    photo_path = student['photo_path']
                    nom = student['nom']
                    postnom = student['postnom']
                    prenom = student['prenom']
                    faculte_nom = student['faculte_nom']
                    promotion = student['promotion']
                    matricule = student['matricule']
                except Exception:
                    student_id = student[0] if len(student) > 0 else None
                    photo_path = student[10] if len(student) > 10 else None
                    nom = student[2] if len(student) > 2 else ''
                    postnom = student[3] if len(student) > 3 else ''
                    prenom = student[4] if len(student) > 4 else ''
                    faculte_nom = student[11] if len(student) > 11 else ''
                    promotion = student[8] if len(student) > 8 else ''
                    matricule = student[1] if len(student) > 1 else ''
                
                if photo_path and os.path.exists(photo_path):
                    students_db[str(student_id)] = {
                        'name': f"{nom} {postnom or ''} {prenom or ''}".strip(),
                        'faculte': faculte_nom or '',
                        'promotion': promotion or '',
                        'matricule': matricule or '',
                        'photo_path': photo_path
                    }
            
            self.face_service.load_student_database(students_db)
            print(f"Base chargée: {len(students_db)} étudiants")
            
        except Exception as e:
            print(f"Erreur chargement étudiants: {e}")
    
    def start_camera(self):
        """Démarrer la caméra"""
        if self.camera_service.start_capture():
            self.update_camera_display()
            self.status_label.config(text="🟢 Caméra active", fg='#28a745')
        else:
            self.status_label.config(text="🔴 Erreur caméra", fg='#dc3545')
            messagebox.showerror("Erreur", "Impossible de démarrer la caméra")
    
    def update_camera_display(self):
        """Mettre à jour l'affichage de la caméra"""
        # Obtenir la frame de la caméra
        frame = self.camera_service.get_frame()
        
        if frame is not None:
            # Traiter la frame avec reconnaissance faciale
            results = self.face_service.process_frame(frame)
            
            # Dessiner les résultats
            frame = self.face_service.draw_results(frame, results)
            
            # Ajouter les informations
            info_text = "Pointage ACTIF" if self.is_running else "Pointage INACTIF"
            frame = self.camera_service.add_info_overlay(frame, info_text)
            
            # Convertir pour Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image = image.resize((640, 480), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image=image)
            
            # Mettre à jour le canvas
            self.video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.video_canvas.image = photo
            
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
                    self.counter_label.config(text=f"Pointages aujourd'hui: {self.attendance_count}")
                    self.feedback_label.config(text=f"✅ Présence marquée: {recognition['name']}", 
                                             fg='#28a745')
            else:
                # Visage non reconnu
                if self.is_running:
                    self.feedback_label.config(text="❌ Visage non reconnu", fg='#dc3545')
                self.reset_student_info()
    
    def update_student_info(self, student_data):
        """Mettre à jour les informations de l'étudiant"""
        self.student_vars['matricule'].set(student_data.get('matricule', ''))
        self.student_vars['nom'].set(student_data.get('name', ''))
        self.student_vars['faculte'].set(student_data.get('faculte', ''))
        self.student_vars['promotion'].set(student_data.get('promotion', ''))
        self.student_vars['confidence'].set(f"{student_data.get('confidence', 0):.2f}")
        
        # Déterminer le statut
        current_time = datetime.now().time()
        if current_time.hour > 8:
            self.student_vars['statut'].set("Retard")
        else:
            self.student_vars['statut'].set("Présent")
    
    def reset_student_info(self):
        """Réinitialiser les informations étudiant"""
        self.student_vars['matricule'].set("Non reconnu")
        self.student_vars['nom'].set("")
        self.student_vars['faculte'].set("")
        self.student_vars['promotion'].set("")
        self.student_vars['confidence'].set("")
        self.student_vars['statut'].set("")
    
    def mark_attendance(self, student_data):
        """Marquer la présence d'un étudiant"""
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
            self.start_btn.config(text="⏸️ PAUSE", bg='#ffc107')
            self.feedback_label.config(text="🟢 Pointage actif - Placez votre visage", fg='#28a745')
        else:
            self.start_btn.config(text="▶️ DÉMARRER", bg='#28a745')
            self.feedback_label.config(text="⏸️ Pointage en pause", fg='#ffc107')
    
    def capture_photo(self):
        """Capturer une photo"""
        try:
            photo_path = self.camera_service.save_frame()
            if photo_path:
                messagebox.showinfo("Photo", f"Photo sauvegardée: {os.path.basename(photo_path)}")
        except Exception as e:
            print(f"Erreur capture photo: {e}")
    
    def add_to_history(self, student_data, status):
        """Ajouter à l'historique"""
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            self.history_tree.insert('', 0, values=(
                current_time,
                student_data.get('matricule', ''),
                student_data.get('name', ''),
                status
            ))
        except Exception as e:
            print(f"Erreur ajout historique: {e}")
    
    def reload_settings(self):
        """Recharger les paramètres de reconnaissance"""
        try:
            # Recharger les paramètres du service
            self.face_service.reload_settings()
            
            # Afficher les infos du nouveau modèle
            model_info = self.face_service.get_model_info()
            
            messagebox.showinfo(
                "Paramètres Rechargés", 
                f"Modèle actuel: {model_info['model_name']}\n"
                f"Précision: {model_info['accuracy']}\n"
                f"Architecture: {model_info['architecture']}\n"
                f"Seuil confiance: {model_info['confidence_threshold']}"
            )
            
            self.feedback_label.config(
                text=f"Modèle rechargé: {model_info['model_name']}", 
                fg='#28a745'
            )
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur rechargement paramètres: {str(e)}")
    
    def on_closing(self):
        """Gérer la fermeture"""
        self.is_running = False
        self.camera_service.stop_capture()
        self.root.destroy()

def main():
    """Test du module pointage"""
    root = tk.Tk()
    
    # Données test
    from database.database import DatabaseUCC
    database = DatabaseUCC()
    
    user_data = {
        'id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    app = AttendanceScreen(root, user_data, database)
    root.mainloop()

if __name__ == "__main__":
    main()
