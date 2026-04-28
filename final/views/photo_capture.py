"""
Fenêtre de capture de photos pour étudiants
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os
import threading
import time

class PhotoCaptureWindow:
    def __init__(self, parent, student_dialog):
        self.parent = parent
        self.student_dialog = student_dialog
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("📸 Capture Photos Étudiant")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.camera = None
        self.is_capturing = False
        self.photos_taken = []
        self.current_photo = 0
        self.countdown = 0
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer la caméra
        self.start_camera()
        
        # Gérer la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        header = tk.Frame(self.window, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="📸 CAPTURE DE PHOTOS - 5 POSITIONS", 
                              font=('Arial', 16, 'bold'), bg='#003366', fg='white')
        title_label.pack(pady=15)
        
        # Contenu principal
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Zone caméra
        camera_frame = tk.LabelFrame(main_frame, text="CAMÉRA", 
                                   font=('Arial', 12, 'bold'), bg='white')
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_canvas = tk.Canvas(camera_frame, width=480, height=360, 
                                    bg='black', highlightthickness=0)
        self.video_canvas.pack(pady=20, padx=20)
        
        # Instructions
        instructions_frame = tk.Frame(camera_frame, bg='white')
        instructions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.instruction_label = tk.Label(instructions_frame, 
                                         text="Positionnez le visage et cliquez sur 'Capturer'", 
                                         font=('Arial', 11), bg='white', fg='#666')
        self.instruction_label.pack()
        
        # Zone de contrôle
        control_frame = tk.LabelFrame(main_frame, text="CONTRÔLE", 
                                     font=('Arial', 12, 'bold'), bg='white')
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Statut
        status_frame = tk.Frame(control_frame, bg='white')
        status_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.status_label = tk.Label(status_frame, text="Photos: 0/5", 
                                     font=('Arial', 14, 'bold'), bg='white', fg='#003366')
        self.status_label.pack()
        
        self.countdown_label = tk.Label(status_frame, text="", 
                                        font=('Arial', 24, 'bold'), bg='white', fg='#dc3545')
        self.countdown_label.pack(pady=10)
        
        # Positions requises
        positions_frame = tk.LabelFrame(control_frame, text="POSITIONS REQUISES", 
                                       font=('Arial', 11, 'bold'), bg='white')
        positions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        positions = [
            "1. Face avant (centre)",
            "2. Profil gauche",
            "3. Profil droit", 
            "4. Légèrement haut",
            "5. Légèrement bas"
        ]
        
        self.position_labels = []
        for i, position in enumerate(positions):
            color = '#28a745' if i < len(self.photos_taken) else '#6c757d'
            label = tk.Label(positions_frame, text=position, font=('Arial', 10), 
                           bg='white', fg=color)
            label.pack(anchor='w', pady=2)
            self.position_labels.append(label)
        
        # Boutons
        buttons_frame = tk.Frame(control_frame, bg='white')
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.capture_btn = tk.Button(buttons_frame, text="📸 Capturer", 
                                    command=self.capture_photo, bg='#17a2b8', fg='white',
                                    font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                                    cursor='hand2', width=15)
        self.capture_btn.pack(pady=5)
        
        self.auto_btn = tk.Button(buttons_frame, text="🔄 Capture Auto", 
                                 command=self.auto_capture, bg='#ffc107', fg='white',
                                 font=('Arial', 11), relief=tk.FLAT, 
                                 cursor='hand2', width=15)
        self.auto_btn.pack(pady=5)
        
        retry_btn = tk.Button(buttons_frame, text="🔄 Recommencer", 
                             command=self.retry_capture, bg='#6c757d', fg='white',
                             font=('Arial', 11), relief=tk.FLAT, 
                             cursor='hand2', width=15)
        retry_btn.pack(pady=5)
        
        # Boutons finaux
        final_buttons_frame = tk.Frame(control_frame, bg='white')
        final_buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.save_btn = tk.Button(final_buttons_frame, text="💾 Enregistrer", 
                                 command=self.save_photos, bg='#28a745', fg='white',
                                 font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                                 cursor='hand2', width=15, state='disabled')
        self.save_btn.pack(pady=5)
        
        cancel_btn = tk.Button(final_buttons_frame, text="❌ Annuler", 
                               command=self.on_closing, bg='#dc3545', fg='white',
                               font=('Arial', 11), relief=tk.FLAT, 
                               cursor='hand2', width=15)
        cancel_btn.pack(pady=5)
    
    def start_camera(self):
        """Démarrer la caméra"""
        try:
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if self.camera.isOpened():
                self.update_camera_display()
            else:
                messagebox.showerror("Erreur", "Impossible d'initialiser la caméra")
                self.on_closing()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur caméra: {str(e)}")
            self.on_closing()
    
    def update_camera_display(self):
        """Mettre à jour l'affichage de la caméra"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            
            if ret:
                # Convertir pour Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                image = image.resize((480, 360), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image=image)
                
                # Mettre à jour le canvas
                self.video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.video_canvas.image = photo
        
        # Planifier la prochaine mise à jour
        if hasattr(self, 'window') and self.window.winfo_exists():
            self.window.after(30, self.update_camera_display)
    
    def capture_photo(self):
        """Capturer une photo"""
        if not self.camera or not self.camera.isOpened():
            messagebox.showerror("Erreur", "Caméra non disponible")
            return
        
        if len(self.photos_taken) >= 5:
            messagebox.showinfo("Info", "5 photos déjà capturées")
            return
        
        try:
            # Capturer l'image
            ret, frame = self.camera.read()
            
            if ret:
                # Convertir et sauvegarder
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                
                # Redimensionner à 224x224 pour DeepFace
                image = image.resize((224, 224), Image.Resampling.LANCZOS)
                
                # Générer le nom du fichier
                student_name = self.student_dialog.generate_student_name()
                photo_filename = f"Dataset/{student_name}_{len(self.photos_taken) + 1}.jpg"
                
                # Sauvegarder
                image.save(photo_filename)
                self.photos_taken.append(photo_filename)
                
                # Mettre à jour l'interface
                self.update_status()
                
                # Mettre à jour le label de position
                self.position_labels[len(self.photos_taken) - 1].config(fg='#28a745')
                
                # Message de succès
                messagebox.showinfo("Succès", f"Photo {len(self.photos_taken)}/5 capturée")
                
                # Activer le bouton sauvegarder si 5 photos
                if len(self.photos_taken) == 5:
                    self.save_btn.config(state='normal')
                    self.capture_btn.config(state='disabled')
                    self.auto_btn.config(state='disabled')
                    self.instruction_label.config(text="✅ Toutes les photos capturées!", fg='#28a745')
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur capture: {str(e)}")
    
    def auto_capture(self):
        """Capture automatique avec décompte"""
        if len(self.photos_taken) >= 5:
            messagebox.showinfo("Info", "5 photos déjà capturées")
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self.auto_capture_thread)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def auto_capture_thread(self):
        """Thread pour capture automatique"""
        positions = ["Face avant", "Profil gauche", "Profil droit", "Légèrement haut", "Légèrement bas"]
        
        for i in range(len(self.photos_taken), 5):
            # Mettre à jour l'instruction
            position_text = positions[i] if i < len(positions) else f"Photo {i+1}"
            
            # Décompte
            for countdown in range(3, 0, -1):
                self.countdown = countdown
                self.window.after(0, lambda c=countdown, p=position_text: 
                                 self.countdown_label.config(text=str(c)))
                self.window.after(0, lambda p=position_text: 
                                 self.instruction_label.config(text=f"{p} - Préparez-vous..."))
                time.sleep(1)
            
            # Capturer
            self.countdown = 0
            self.window.after(0, lambda: self.countdown_label.config(text=""))
            self.window.after(0, lambda: self.capture_photo())
            
            # Pause entre les photos
            if i < 4:
                time.sleep(2)
        
        self.is_capturing = False
    
    def retry_capture(self):
        """Recommencer la capture"""
        if messagebox.askyesno("Confirmation", "Voulez-vous effacer toutes les photos et recommencer ?"):
            # Supprimer les fichiers
            for photo_path in self.photos_taken:
                try:
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                except:
                    pass
            
            # Réinitialiser
            self.photos_taken = []
            self.update_status()
            
            # Réinitialiser les labels
            for label in self.position_labels:
                label.config(fg='#6c757d')
            
            # Réactiver les boutons
            self.capture_btn.config(state='normal')
            self.auto_btn.config(state='normal')
            self.save_btn.config(state='disabled')
            
            self.instruction_label.config(text="Positionnez le visage et cliquez sur 'Capturer'", fg='#666')
    
    def update_status(self):
        """Mettre à jour le statut"""
        self.status_label.config(text=f"Photos: {len(self.photos_taken)}/5")
        self.student_dialog.photo_status.set(f"{len(self.photos_taken)} photos capturées")
    
    def save_photos(self):
        """Sauvegarder les photos et fermer"""
        if len(self.photos_taken) != 5:
            messagebox.showwarning("Attention", "Veuillez capturer 5 photos")
            return
        
        # Transférer les photos au dialogue parent
        self.student_dialog.student_photos = self.photos_taken.copy()
        self.student_dialog.photo_count = len(self.photos_taken)
        self.student_dialog.photo_status.set(f"{len(self.photos_taken)} photos prêtes")
        
        messagebox.showinfo("Succès", "Photos enregistrées avec succès!")
        self.on_closing()
    
    def on_closing(self):
        """Fermer la fenêtre"""
        self.is_capturing = False
        
        if self.camera:
            self.camera.release()
        
        self.window.destroy()

class PhotoViewWindow:
    """Fenêtre pour visualiser les photos capturées"""
    
    def __init__(self, parent, photos):
        self.parent = parent
        self.photos = photos
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("👁️ Visualisation Photos")
        self.window.geometry("800x600")
        self.window.transient(parent)
        
        # Variables
        self.current_photo = 0
        
        # Créer l'interface
        self.setup_ui()
        
        # Afficher la première photo
        self.display_photo()
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        header = tk.Frame(self.window, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=f"👁️ PHOTOS ({len(self.photos)}/5)", 
                              font=('Arial', 16, 'bold'), bg='#003366', fg='white')
        title_label.pack(pady=15)
        
        # Contenu principal
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Zone photo
        photo_frame = tk.Frame(main_frame, bg='white')
        photo_frame.pack(fill=tk.BOTH, expand=True)
        
        self.photo_canvas = tk.Canvas(photo_frame, bg='black', highlightthickness=0)
        self.photo_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Contrôles
        controls_frame = tk.Frame(main_frame, bg='white')
        controls_frame.pack(fill=tk.X, pady=20)
        
        # Navigation
        nav_frame = tk.Frame(controls_frame, bg='white')
        nav_frame.pack()
        
        self.prev_btn = tk.Button(nav_frame, text="◀ Précédent", 
                                  command=self.prev_photo, bg='#6c757d', fg='white',
                                  font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.photo_label = tk.Label(nav_frame, text="Photo 1/5", 
                                    font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        self.photo_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = tk.Button(nav_frame, text="Suivant ▶", 
                                  command=self.next_photo, bg='#6c757d', fg='white',
                                  font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton fermer
        close_btn = tk.Button(controls_frame, text="Fermer", command=self.window.destroy,
                              bg='#dc3545', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        close_btn.pack(pady=10)
    
    def display_photo(self):
        """Afficher la photo actuelle"""
        if not self.photos:
            return
        
        try:
            from PIL import Image, ImageTk
            
            photo_path = self.photos[self.current_photo]
            image = Image.open(photo_path)
            
            # Redimensionner pour l'affichage
            canvas_width = self.photo_canvas.winfo_width()
            canvas_height = self.photo_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image=image)
            
            # Centrer l'image
            self.photo_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                anchor=tk.CENTER, image=photo
            )
            self.photo_canvas.image = photo
            
            # Mettre à jour le label
            self.photo_label.config(text=f"Photo {self.current_photo + 1}/{len(self.photos)}")
            
            # Mettre à jour les boutons
            self.prev_btn.config(state='normal' if self.current_photo > 0 else 'disabled')
            self.next_btn.config(state='normal' if self.current_photo < len(self.photos) - 1 else 'disabled')
            
        except Exception as e:
            print(f"Erreur affichage photo: {e}")
    
    def prev_photo(self):
        """Photo précédente"""
        if self.current_photo > 0:
            self.current_photo -= 1
            self.display_photo()
    
    def next_photo(self):
        """Photo suivante"""
        if self.current_photo < len(self.photos) - 1:
            self.current_photo += 1
            self.display_photo()
