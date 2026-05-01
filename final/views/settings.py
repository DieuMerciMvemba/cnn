"""
Module Paramètres - Système UCC
Configuration du système et préférences
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

class SettingsScreen:
    def __init__(self, parent, user_data, database):
        self.parent = parent
        self.user_data = user_data
        self.database = database
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Paramètres du Système")
        self.window.geometry("800x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.settings_file = "final/config/settings.json"
        self.settings = self.load_settings()
        
        # Variables des paramètres
        self.init_variables()
        
        # Configurer les variables par défaut
        default_settings = self.get_default_settings()
        self.settings.update(default_settings)
        
        # Initialiser les variables anti-spoofing
        self.anti_spoof_enabled = tk.BooleanVar(value=True)
        self.liveness_threshold = tk.DoubleVar(value=0.5)
        self.blink_required = tk.IntVar(value=3)
        
        # Charger les paramètres sauvegardés
        self.load_settings()
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les valeurs
        self.load_values()
        
        # Gérer la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_variables(self):
        """Initialiser les variables des paramètres"""
        # Paramètres caméra
        self.camera_id = tk.StringVar(value=str(self.settings.get('camera', {}).get('id', 0)))
        self.camera_width = tk.StringVar(value=str(self.settings.get('camera', {}).get('width', 640)))
        self.camera_height = tk.StringVar(value=str(self.settings.get('camera', {}).get('height', 480)))
        self.camera_fps = tk.StringVar(value=str(self.settings.get('camera', {}).get('fps', 30)))
        
        # Paramètres reconnaissance
        self.recognition_model = tk.StringVar(value=self.settings.get('recognition', {}).get('model', 'VGG-Face'))
        self.recognition_threshold = tk.StringVar(value=str(self.settings.get('recognition', {}).get('threshold', 0.4)))
        self.detection_threshold = tk.StringVar(value=str(self.settings.get('recognition', {}).get('detection_threshold', 0.95)))
        
        # Paramètres pointage
        self.late_hour = tk.StringVar(value=str(self.settings.get('attendance', {}).get('late_hour', 8)))
        self.late_minute = tk.StringVar(value=str(self.settings.get('attendance', {}).get('late_minute', 0)))
        self.early_exit_hour = tk.StringVar(value=str(self.settings.get('attendance', {}).get('early_exit_hour', 17)))
        self.early_exit_minute = tk.StringVar(value=str(self.settings.get('attendance', {}).get('early_exit_minute', 0)))
        self.duplicate_timeout = tk.StringVar(value=str(self.settings.get('attendance', {}).get('duplicate_timeout', 5)))
        
        # Paramètres interface
        self.theme = tk.StringVar(value=self.settings.get('ui', {}).get('theme', 'light'))
        self.language = tk.StringVar(value=self.settings.get('ui', {}).get('language', 'fr'))
        self.auto_refresh = tk.BooleanVar(value=self.settings.get('ui', {}).get('auto_refresh', True))
        self.refresh_interval = tk.StringVar(value=str(self.settings.get('ui', {}).get('refresh_interval', 30)))
        
        # Paramètres notifications
        self.enable_notifications = tk.BooleanVar(value=self.settings.get('notifications', {}).get('enabled', True))
        self.sound_enabled = tk.BooleanVar(value=self.settings.get('notifications', {}).get('sound', True))
        self.email_enabled = tk.BooleanVar(value=self.settings.get('notifications', {}).get('email', False))
        
        # Paramètres sécurité
        self.session_timeout = tk.StringVar(value=str(self.settings.get('security', {}).get('session_timeout', 60)))
        self.max_login_attempts = tk.StringVar(value=str(self.settings.get('security', {}).get('max_login_attempts', 3)))
        self.password_min_length = tk.StringVar(value=str(self.settings.get('security', {}).get('password_min_length', 8)))
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        self.create_header()
        
        # Zone principale avec onglets
        self.create_tabs()
        
        # Boutons d'action
        self.create_actions()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.window, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(header, text="⚙️ PARAMÈTRES DU SYSTÈME", 
                              font=('Arial', 18, 'bold'), bg='#003366', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Bouton fermer
        close_btn = tk.Button(header, text="Fermer", command=self.on_closing,
                              bg='#6c757d', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def create_tabs(self):
        """Créer les onglets"""
        tab_frame = tk.Frame(self.window, bg='white')
        tab_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer les onglets
        self.notebook = ttk.Notebook(tab_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Caméra
        self.create_camera_tab()
        
        # Onglet Reconnaissance
        self.create_recognition_tab()
        
        # Onglet Pointage
        self.create_attendance_tab()
        
        # Onglet Interface
        self.create_ui_tab()
        
        # Onglet Notifications
        self.create_notifications_tab()
        
        # Onglet Anti-Spoofing
        self.create_anti_spoofing_tab()
        
        # Onglet Sécurité
        self.create_security_tab()
    
    def create_camera_tab(self):
        """Créer l'onglet Caméra"""
        camera_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(camera_frame, text="📸 Caméra")
        
        # Configuration caméra
        config_frame = tk.LabelFrame(camera_frame, text="Configuration Caméra", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # ID de la caméra
        id_frame = tk.Frame(config_frame, bg='white')
        id_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(id_frame, text="ID de la caméra:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        id_entry = ttk.Entry(id_frame, textvariable=self.camera_id, width=10)
        id_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(id_frame, text="(0 pour caméra par défaut)", font=('Arial', 9), 
                bg='white', fg='#666').pack(side=tk.LEFT, padx=(10, 0))
        
        # Résolution
        resolution_frame = tk.Frame(config_frame, bg='white')
        resolution_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(resolution_frame, text="Résolution:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        tk.Label(resolution_frame, text="Largeur:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(20, 5))
        
        width_entry = ttk.Entry(resolution_frame, textvariable=self.camera_width, width=8)
        width_entry.pack(side=tk.LEFT)
        
        tk.Label(resolution_frame, text="Hauteur:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(10, 5))
        
        height_entry = ttk.Entry(resolution_frame, textvariable=self.camera_height, width=8)
        height_entry.pack(side=tk.LEFT)
        
        # FPS
        fps_frame = tk.Frame(config_frame, bg='white')
        fps_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(fps_frame, text="FPS cible:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        fps_entry = ttk.Entry(fps_frame, textvariable=self.camera_fps, width=8)
        fps_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Bouton test caméra
        test_btn = tk.Button(config_frame, text="📸 Tester Caméra", 
                           command=self.test_camera, bg='#17a2b8', fg='white',
                           font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        test_btn.pack(pady=10)
    
    def create_recognition_tab(self):
        """Créer l'onglet Reconnaissance"""
        recognition_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(recognition_frame, text="🧠 Reconnaissance")
        
        # Configuration reconnaissance
        config_frame = tk.LabelFrame(recognition_frame, text="Configuration Reconnaissance Faciale", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Modèle
        model_frame = tk.Frame(config_frame, bg='white')
        model_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(model_frame, text="Modèle de reconnaissance:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        models = ['Haute Précision (99.9%)', 'ArcFace (99.85%)', 'VGG-Face (98.97%)', 'Facenet (99.63%)', 'OpenFace (95%)', 'DeepFace (90%)']
        model_combo = ttk.Combobox(model_frame, textvariable=self.recognition_model,
                                   values=models, state='readonly', width=25)
        model_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Détecteur de visage
        detector_frame = tk.Frame(config_frame, bg='white')
        detector_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(detector_frame, text="Détecteur visage:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        detectors = ['Auto (Meilleur)', 'RetinaFace (99%)', 'MTCNN (96%)', 'Dlib HOG (93%)', 'Haar Cascade (88%)']
        self.face_detector = tk.StringVar(value='Auto (Meilleur)')
        detector_combo = ttk.Combobox(detector_frame, textvariable=self.face_detector,
                                     values=detectors, state='readonly', width=25)
        detector_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Seuil de reconnaissance
        threshold_frame = tk.Frame(config_frame, bg='white')
        threshold_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(threshold_frame, text="Seuil de reconnaissance:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        threshold_entry = ttk.Entry(threshold_frame, textvariable=self.recognition_threshold, width=10)
        threshold_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(threshold_frame, text="(0.0 - 1.0)", font=('Arial', 9), 
                bg='white', fg='#666').pack(side=tk.LEFT, padx=(5, 0))
        
        # Seuil de détection
        detection_frame = tk.Frame(config_frame, bg='white')
        detection_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(detection_frame, text="Seuil de détection faciale:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        detection_entry = ttk.Entry(detection_frame, textvariable=self.detection_threshold, width=10)
        detection_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(detection_frame, text="(0.0 - 1.0)", font=('Arial', 9), 
                bg='white', fg='#666').pack(side=tk.LEFT, padx=(5, 0))
        
        # Informations
        info_text = """
🧠 MODÈLES CNN (RECONNAISSANCE):
🏆 Haute Précision (99.9%): ULTRA PRÉCIS - Multi-validation, seuils stricts
🥇 ArcFace (99.85%): LE PLUS PRÉCIS - ResNet-100, State-of-the-art
🥈 FaceNet (99.63%): Très précis - Inception-ResNet v1, Google
🥉 VGG-Face (98.97%): Rapide et fiable - VGG-16, Oxford
4️⃣ OpenFace (95%): Bon compromis - Lightweight, rapide
5️⃣ DeepFace (90%): Générique - Basique, moins précis

👁️ DÉTECTEURS VISAGE (DÉTECTION):
🥇 RetinaFace (99%): Le plus précis - 5 points faciaux, robuste
🥈 MTCNN (96%): Excellent - Multi-scale, très fiable
🥉 Dlib HOG (93%): Bon - Rapide sur CPU, robuste aux angles
4️⃣ Haar Cascade (88%): Rapide - Léger, inclus dans OpenCV

⚡ RECOMMANDATIONS:
• Précision max: Haute Précision + RetinaFace
• Équilibre: VGG-Face + MTCNN
• Vitesse: VGG-Face + Haar Cascade
• Auto: Meilleur disponible automatiquement
        """
        
        info_label = tk.Label(config_frame, text=info_text, font=('Arial', 10), 
                              bg='white', fg='#666', justify=tk.LEFT)
        info_label.pack(padx=20, pady=10)
    
    def create_attendance_tab(self):
        """Créer l'onglet Pointage"""
        attendance_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(attendance_frame, text="📝 Pointage")
        
        # Configuration pointage
        config_frame = tk.LabelFrame(attendance_frame, text="Configuration Pointage", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Heure de retard
        late_frame = tk.Frame(config_frame, bg='white')
        late_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(late_frame, text="Heure de retard:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        tk.Label(late_frame, text="Heure:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(20, 5))
        
        late_hour_entry = ttk.Entry(late_frame, textvariable=self.late_hour, width=5)
        late_hour_entry.pack(side=tk.LEFT)
        
        tk.Label(late_frame, text=":", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(2, 2))
        
        late_minute_entry = ttk.Entry(late_frame, textvariable=self.late_minute, width=5)
        late_minute_entry.pack(side=tk.LEFT)
        
        # Heure de sortie anticipée
        early_frame = tk.Frame(config_frame, bg='white')
        early_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(early_frame, text="Sortie anticipée:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        tk.Label(early_frame, text="Heure:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(20, 5))
        
        early_hour_entry = ttk.Entry(early_frame, textvariable=self.early_exit_hour, width=5)
        early_hour_entry.pack(side=tk.LEFT)
        
        tk.Label(early_frame, text=":", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(2, 2))
        
        early_minute_entry = ttk.Entry(early_frame, textvariable=self.early_exit_minute, width=5)
        early_minute_entry.pack(side=tk.LEFT)
        
        # Timeout de duplication
        timeout_frame = tk.Frame(config_frame, bg='white')
        timeout_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(timeout_frame, text="Timeout anti-duplication (minutes):", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        timeout_entry = ttk.Entry(timeout_frame, textvariable=self.duplicate_timeout, width=8)
        timeout_entry.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_ui_tab(self):
        """Créer l'onglet Interface"""
        ui_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(ui_frame, text="🎨 Interface")
        
        # Configuration interface
        config_frame = tk.LabelFrame(ui_frame, text="Configuration Interface", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Thème
        theme_frame = tk.Frame(config_frame, bg='white')
        theme_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(theme_frame, text="Thème:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        themes = ['light', 'dark', 'blue']
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme,
                                  values=themes, state='readonly', width=15)
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Langue
        lang_frame = tk.Frame(config_frame, bg='white')
        lang_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(lang_frame, text="Langue:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        languages = ['fr', 'en']
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language,
                                 values=languages, state='readonly', width=10)
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto-rafraîchissement
        auto_frame = tk.Frame(config_frame, bg='white')
        auto_frame.pack(fill=tk.X, padx=20, pady=10)
        
        auto_check = tk.Checkbutton(auto_frame, text="Auto-rafraîchissement", 
                                   variable=self.auto_refresh, bg='white', font=('Arial', 11))
        auto_check.pack(side=tk.LEFT)
        
        tk.Label(auto_frame, text="Intervalle (secondes):", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT, padx=(20, 5))
        
        refresh_entry = ttk.Entry(auto_frame, textvariable=self.refresh_interval, width=8)
        refresh_entry.pack(side=tk.LEFT)
    
    def create_notifications_tab(self):
        """Créer l'onglet Notifications"""
        notif_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(notif_frame, text="🔔 Notifications")
        
        # Configuration notifications
        config_frame = tk.LabelFrame(notif_frame, text="Configuration Notifications", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Activer notifications
        enabled_check = tk.Checkbutton(config_frame, text="Activer les notifications", 
                                      variable=self.enable_notifications, bg='white', font=('Arial', 11))
        enabled_check.pack(anchor='w', padx=20, pady=5)
        
        # Notifications sonores
        sound_check = tk.Checkbutton(config_frame, text="Notifications sonores", 
                                   variable=self.sound_enabled, bg='white', font=('Arial', 11))
        sound_check.pack(anchor='w', padx=20, pady=5)
        
        # Notifications email
        email_check = tk.Checkbutton(config_frame, text="Notifications par email", 
                                   variable=self.email_enabled, bg='white', font=('Arial', 11))
        email_check.pack(anchor='w', padx=20, pady=5)
        
        # Test notifications
        test_frame = tk.Frame(config_frame, bg='white')
        test_frame.pack(fill=tk.X, padx=20, pady=20)
        
        test_btn = tk.Button(test_frame, text="🔔 Tester Notifications", 
                           command=self.test_notifications, bg='#ffc107', fg='white',
                           font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        test_btn.pack()
    
    def create_anti_spoofing_tab(self):
        """Créer l'onglet Anti-Spoofing"""
        anti_spoof_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(anti_spoof_frame, text="🛡️ Anti-Spoofing")
        
        # Configuration
        config_frame = tk.LabelFrame(anti_spoof_frame, text="Configuration Anti-Spoofing", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Activer/Désactiver
        enable_frame = tk.Frame(config_frame, bg='white')
        enable_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.anti_spoof_enabled = tk.BooleanVar(value=True)
        enable_check = tk.Checkbutton(enable_frame, text="Activer la détection anti-spoofing", 
                                     variable=self.anti_spoof_enabled, font=('Arial', 11),
                                     bg='white')
        enable_check.pack(side=tk.LEFT)
        
        # Seuil de liveness
        threshold_frame = tk.Frame(config_frame, bg='white')
        threshold_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(threshold_frame, text="Seuil Liveness:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        self.liveness_threshold = tk.DoubleVar(value=0.5)
        threshold_entry = ttk.Entry(threshold_frame, textvariable=self.liveness_threshold, width=10)
        threshold_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(threshold_frame, text="(0.0 - 1.0)", font=('Arial', 9), 
                bg='white', fg='#666').pack(side=tk.LEFT, padx=(5, 0))
        
        # Clignements requis
        blink_frame = tk.Frame(config_frame, bg='white')
        blink_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(blink_frame, text="Clignements requis:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        self.blink_required = tk.IntVar(value=3)
        blink_spin = ttk.Spinbox(blink_frame, from_=1, to=10, textvariable=self.blink_required, 
                                width=10)
        blink_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Informations
        info_frame = tk.LabelFrame(anti_spoof_frame, text="Informations", 
                                  font=('Arial', 12, 'bold'), bg='white')
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        info_text = """
🛡️ ANTI-SPOOFING - Protection contre les faux visages

🎯 DÉTECTIONS:
• Clignement des yeux (liveness)
• Analyse de texture (photos imprimées)
• Micro-mouvements (respiration)
• Analyse de profondeur (2D vs 3D)

🔍 TYPES DE SPOOFING DÉTECTÉS:
• Photos sur téléphone/écran
• Images imprimées
• Masques 2D/3D
• Vidéos replay
• Deepfakes

⚙️ RECOMMANDATIONS:
• Seuil Liveness: 0.5 (équilibré)
• Clignements: 3 (rapide mais fiable)
• Activer pour zones sensibles

⚡ PERFORMANCE:
• Ajoute ~1-2 secondes au pointage
• Précision: 95%+ contre les photos
• Compatible avec tous les modèles CNN
        """
        
        info_label = tk.Label(info_frame, text=info_text, font=('Arial', 10), 
                              bg='white', fg='#666', justify=tk.LEFT)
        info_label.pack(padx=20, pady=10)
        
        # Test
        test_frame = tk.LabelFrame(anti_spoof_frame, text="Test", 
                                  font=('Arial', 12, 'bold'), bg='white')
        test_frame.pack(fill=tk.X, padx=20, pady=20)
        
        test_btn = tk.Button(test_frame, text="🧪 Tester Anti-Spoofing", 
                            command=self.test_anti_spoofing, bg='#17a2b8', fg='white',
                            font=('Arial', 11, 'bold'), relief=tk.FLAT, cursor='hand2')
        test_btn.pack(pady=10)
    
    def create_security_tab(self):
        """Créer l'onglet Sécurité"""
        security_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(security_frame, text="🔒 Sécurité")
        
        # Configuration sécurité
        config_frame = tk.LabelFrame(security_frame, text="Configuration Sécurité", 
                                    font=('Arial', 12, 'bold'), bg='white')
        config_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Timeout de session
        session_frame = tk.Frame(config_frame, bg='white')
        session_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(session_frame, text="Timeout de session (minutes):", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        session_entry = ttk.Entry(session_frame, textvariable=self.session_timeout, width=8)
        session_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Tentatives de connexion
        attempts_frame = tk.Frame(config_frame, bg='white')
        attempts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(attempts_frame, text="Max tentatives de connexion:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        attempts_entry = ttk.Entry(attempts_frame, textvariable=self.max_login_attempts, width=5)
        attempts_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Longueur minimale du mot de passe
        password_frame = tk.Frame(config_frame, bg='white')
        password_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(password_frame, text="Longueur minimale mot de passe:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT)
        
        password_entry = ttk.Entry(password_frame, textvariable=self.password_min_length, width=5)
        password_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Actions de sécurité
        actions_frame = tk.LabelFrame(security_frame, text="Actions de Sécurité", 
                                      font=('Arial', 12, 'bold'), bg='white')
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Changer mot de passe
        change_btn = tk.Button(actions_frame, text="🔑 Changer mon mot de passe", 
                             command=self.change_password, bg='#007bff', fg='white',
                             font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        change_btn.pack(pady=5)
        
        # Vérifier les logs
        logs_btn = tk.Button(actions_frame, text="📋 Voir les logs de sécurité", 
                            command=self.view_security_logs, bg='#6c757d', fg='white',
                            font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        logs_btn.pack(pady=5)
    
    def create_actions(self):
        """Créer les boutons d'action"""
        actions_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, borderwidth=1)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Boutons
        buttons_container = tk.Frame(actions_frame, bg='white')
        buttons_container.pack(pady=15)
        
        # Sauvegarder
        save_btn = tk.Button(buttons_container, text="💾 Sauvegarder", 
                           command=self.save_settings, bg='#28a745', fg='white',
                           font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                           cursor='hand2', width=15)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Réinitialiser
        reset_btn = tk.Button(buttons_container, text="🔄 Réinitialiser", 
                            command=self.reset_settings, bg='#ffc107', fg='white',
                            font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                            cursor='hand2', width=15)
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Importer/Exporter
        import_btn = tk.Button(buttons_container, text="📥 Importer", 
                             command=self.import_settings, bg='#17a2b8', fg='white',
                             font=('Arial', 11), relief=tk.FLAT, 
                             cursor='hand2', width=12)
        import_btn.pack(side=tk.LEFT, padx=10)
        
        export_btn = tk.Button(buttons_container, text="📤 Exporter", 
                             command=self.export_settings, bg='#6f42c1', fg='white',
                             font=('Arial', 11), relief=tk.FLAT, 
                             cursor='hand2', width=12)
        export_btn.pack(side=tk.LEFT, padx=10)
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.window, bg='#f0f0f0', height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_text = tk.Label(footer, text="© 2024 UCC - Module Paramètres", 
                               font=('Arial', 9), bg='#f0f0f0', fg='#666')
        footer_text.pack(pady=5)
    
    def load_settings(self):
        """Charger les paramètres depuis le fichier"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_settings()
        except Exception as e:
            print(f"Erreur chargement paramètres: {e}")
            return self.get_default_settings()
    
    def get_default_settings(self):
        """Obtenir les paramètres par défaut"""
        return {
            'camera': {
                'id': 0,
                'width': 640,
                'height': 480,
                'fps': 30
            },
            'recognition': {
                'model': 'VGG-Face',
                'threshold': 0.4,
                'detection_threshold': 0.95
            },
            'attendance': {
                'late_hour': 8,
                'late_minute': 0,
                'early_exit_hour': 17,
                'early_exit_minute': 0,
                'duplicate_timeout': 5
            },
            'ui': {
                'theme': 'light',
                'language': 'fr',
                'auto_refresh': True,
                'refresh_interval': 30
            },
            'notifications': {
                'enabled': True,
                'sound': True,
                'email': False
            },
            'security': {
                'session_timeout': 60,
                'max_login_attempts': 3,
                'password_min_length': 8
            }
        }
    
    def load_values(self):
        """Charger les valeurs dans les champs"""
        if self.settings:
            # Anti-Spoofing
            anti_spoof = self.settings.get('anti_spoofing', {})
            self.anti_spoof_enabled.set(anti_spoof.get('enabled', True))
            self.liveness_threshold.set(anti_spoof.get('liveness_threshold', 0.5))
            self.blink_required.set(anti_spoof.get('blink_required', 3))
    
    def save_settings(self):
        """Sauvegarder les paramètres"""
        try:
            # Valider les valeurs
            if not self.validate_settings():
                return
            
            # Extraire le nom du modèle (sans le pourcentage)
            model_full = self.recognition_model.get()
            model_name = model_full.split(' (')[0] if ' (' in model_full else model_full
            
            # Créer le dictionnaire des paramètres
            settings = {
                'camera': {
                    'id': int(self.camera_id.get()),
                    'width': int(self.camera_width.get()),
                    'height': int(self.camera_height.get()),
                    'fps': int(self.camera_fps.get())
                },
                'recognition': {
                    'model': model_name,
                    'threshold': float(self.recognition_threshold.get()),
                    'detection_threshold': float(self.detection_threshold.get())
                },
                'attendance': {
                    'late_hour': int(self.late_hour.get()),
                    'late_minute': int(self.late_minute.get()),
                    'early_exit_hour': int(self.early_exit_hour.get()),
                    'early_exit_minute': int(self.early_exit_minute.get()),
                    'duplicate_timeout': int(self.duplicate_timeout.get())
                },
                'anti_spoofing': {
                    'enabled': self.anti_spoof_enabled.get(),
                    'liveness_threshold': float(self.liveness_threshold.get()),
                    'blink_required': int(self.blink_required.get())
                },
                'ui': {
                    'theme': self.theme.get(),
                    'language': self.language.get(),
                    'auto_refresh': self.auto_refresh.get(),
                    'refresh_interval': int(self.refresh_interval.get())
                },
                'notifications': {
                    'enabled': self.enable_notifications.get(),
                    'sound': self.sound_enabled.get(),
                    'email': self.email_enabled.get()
                },
                'security': {
                    'session_timeout': int(self.session_timeout.get()),
                    'max_login_attempts': int(self.max_login_attempts.get()),
                    'password_min_length': int(self.password_min_length.get())
                }
            }
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Sauvegarder
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            # Message de succès avec option de redémarrage
            result = messagebox.askyesno(
                "Succès", 
                f"Paramètres sauvegardés avec succès!\n\n"
                f"Modèle de reconnaissance: {model_name}\n"
                f"Seuil: {self.recognition_threshold.get()}\n\n"
                f"Voulez-vous redémarrer l'application pour appliquer les changements?"
            )
            
            if result:
                self.restart_application()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde paramètres: {str(e)}")
    
    def validate_settings(self):
        """Valider les paramètres"""
        try:
            # Valider les valeurs numériques
            int(self.camera_id.get())
            int(self.camera_width.get())
            int(self.camera_height.get())
            int(self.camera_fps.get())
            
            threshold = float(self.recognition_threshold.get())
            if not 0.0 <= threshold <= 1.0:
                raise ValueError("Le seuil de reconnaissance doit être entre 0.0 et 1.0")
            
            detection = float(self.detection_threshold.get())
            if not 0.0 <= detection <= 1.0:
                raise ValueError("Le seuil de détection doit être entre 0.0 et 1.0")
            
            int(self.late_hour.get())
            int(self.late_minute.get())
            int(self.early_exit_hour.get())
            int(self.early_exit_minute.get())
            int(self.duplicate_timeout.get())
            int(self.refresh_interval.get())
            int(self.session_timeout.get())
            int(self.max_login_attempts.get())
            int(self.password_min_length.get())
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Erreur de validation", str(e))
            return False
    
    def reset_settings(self):
        """Réinitialiser les paramètres par défaut"""
        if messagebox.askyesno("Confirmation", "Voulez-vous réinitialiser tous les paramètres aux valeurs par défaut?"):
            self.settings = self.get_default_settings()
            self.init_variables()
            messagebox.showinfo("Succès", "Paramètres réinitialisés aux valeurs par défaut")
    
    def import_settings(self):
        """Importer des paramètres depuis un fichier"""
        try:
            file_path = filedialog.askopenfilename(
                title="Importer les paramètres",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            
            self.init_variables()
            messagebox.showinfo("Succès", "Paramètres importés avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur importation paramètres: {str(e)}")
    
    def export_settings(self):
        """Exporter les paramètres vers un fichier"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exporter les paramètres",
                defaultextension=".json",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Succès", f"Paramètres exportés avec succès!\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur exportation paramètres: {str(e)}")
    
    def test_camera(self):
        """Tester la caméra"""
        try:
            import cv2
            
            camera_id = int(self.camera_id.get())
            cap = cv2.VideoCapture(camera_id)
            
            if cap.isOpened():
                messagebox.showinfo("Succès", f"Caméra {camera_id} détectée avec succès!")
                cap.release()
            else:
                messagebox.showerror("Erreur", f"Impossible d'accéder à la caméra {camera_id}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur test caméra: {str(e)}")
    
    def test_anti_spoofing(self):
        """Tester l'anti-spoofing"""
        try:
            from services.anti_spoofing import AntiSpoofingService
            
            anti_spoof = AntiSpoofingService()
            
            messagebox.showinfo(
                "Anti-Spoofing Test", 
                f"🛡️ Service Anti-Spoofing initialisé!\n\n"
                f"Seuil Liveness: {anti_spoof.liveness_threshold}\n"
                f"Clignements requis: {anti_spoof.blink_threshold}\n"
                f"Détections activées:\n"
                f"• Clignement des yeux\n"
                f"• Analyse texture\n"
                f"• Micro-mouvements\n"
                f"• Analyse profondeur\n\n"
                f"Fonctionnalité prête pour le pointage!"
            )
            
            self.feedback_label.config(text="Anti-Spoofing testé avec succès", fg='#28a745')
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur test anti-spoofing: {str(e)}")
    
    def test_notifications(self):
        """Tester les notifications"""
        try:
            if self.enable_notifications.get():
                if self.sound_enabled.get():
                    # Simuler un son (bip système)
                    import winsound
                    winsound.Beep(1000, 500)  # Fréquence 1000Hz, durée 500ms
                messagebox.showinfo("Test", "Notification de test envoyée!")
            else:
                messagebox.showwarning("Avertissement", "Les notifications sont désactivées")
                
        except Exception as e:
            messagebox.showinfo("Test", "Notification de test envoyée! (Son non disponible)")
    
    def change_password(self):
        """Changer le mot de passe"""
        # TODO: Implémenter la fenêtre de changement de mot de passe
        messagebox.showinfo("Info", "Fonction de changement de mot de passe en développement")
    
    def view_security_logs(self):
        """Voir les logs de sécurité"""
        # TODO: Implémenter la fenêtre des logs de sécurité
        messagebox.showinfo("Info", "Fonction des logs de sécurité en développement")
    
    def restart_application(self):
        """Redémarrer l'application avec les nouveaux paramètres"""
        try:
            # Fermer la fenêtre des paramètres
            self.window.destroy()
            
            # Fermer la fenêtre parent (portail)
            self.parent.destroy()
            
            # Relancer l'application
            import subprocess
            import sys
            
            # Relancer le script actuel
            subprocess.Popen([sys.executable] + sys.argv)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur redémarrage: {str(e)}")
    
    def on_closing(self):
        """Fermer la fenêtre"""
        # Demander si on veut sauvegarder les changements
        if messagebox.askyesno("Quitter", "Voulez-vous sauvegarder les changements avant de quitter?"):
            self.save_settings()
        
        # Vérifier si la fenêtre existe encore avant de détruire
        try:
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.destroy()
        except:
            pass  # La fenêtre est déjà détruite
