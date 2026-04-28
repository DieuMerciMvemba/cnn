"""
Module Gestion des Étudiants - Système UCC
Interface complète pour gérer les étudiants
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import cv2
from datetime import datetime

class StudentsScreen:
    def __init__(self, root, user_data, database):
        self.root = root
        self.user_data = user_data
        self.database = database
        
        # Variables
        self.search_var = tk.StringVar()
        self.faculty_filter = tk.StringVar()
        self.promotion_filter = tk.StringVar()
        self.current_student = None
        
        # Configuration fenêtre
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données
        self.load_faculties()
        self.load_students()
        
        # Bind events
        self.search_var.trace('w', self.filter_students)
        self.faculty_filter.trace('w', self.filter_students)
        self.promotion_filter.trace('w', self.filter_students)
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        self.create_header()
        
        # Filtres et recherche
        self.create_filters()
        
        # Liste des étudiants
        self.create_students_list()
        
        # Frame détails (caché au début)
        self.details_frame = None
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.root, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(header, text="👥 GESTION DES ÉTUDIANTS", 
                              font=('Arial', 18, 'bold'), bg='#003366', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Boutons actions
        actions_frame = tk.Frame(header, bg='#003366')
        actions_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        add_btn = tk.Button(actions_frame, text="+ Ajouter", command=self.add_student,
                           bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                           relief=tk.FLAT, cursor='hand2')
        add_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = tk.Button(actions_frame, text="📥 Importer", command=self.import_students,
                              bg='#17a2b8', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        import_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = tk.Button(actions_frame, text="📤 Exporter", command=self.export_students,
                              bg='#6f42c1', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        export_btn.pack(side=tk.LEFT, padx=5)
    
    def create_filters(self):
        """Créer les filtres et recherche"""
        filter_frame = tk.Frame(self.root, bg='white', relief=tk.RAISED, borderwidth=1)
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Recherche
        search_frame = tk.Frame(filter_frame, bg='white')
        search_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        search_label = tk.Label(search_frame, text="🔍 Rechercher:", 
                                font=('Arial', 11), bg='white')
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                                 font=('Arial', 11), width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Filtres
        filters_container = tk.Frame(filter_frame, bg='white')
        filters_container.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Filtre faculté
        faculty_label = tk.Label(filters_container, text="Faculté:", 
                                font=('Arial', 11), bg='white')
        faculty_label.pack(side=tk.LEFT, padx=(0, 5))
        
        faculty_combo = ttk.Combobox(filters_container, textvariable=self.faculty_filter,
                                    font=('Arial', 10), width=20, state='readonly')
        faculty_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Filtre promotion
        promotion_label = tk.Label(filters_container, text="Promotion:", 
                                 font=('Arial', 11), bg='white')
        promotion_label.pack(side=tk.LEFT, padx=(0, 5))
        
        promotion_combo = ttk.Combobox(filters_container, textvariable=self.promotion_filter,
                                      font=('Arial', 10), width=15, state='readonly')
        promotion_combo.pack(side=tk.LEFT)
        
        # Stocker les combobox
        self.faculty_combo = faculty_combo
        self.promotion_combo = promotion_combo
    
    def create_students_list(self):
        """Créer la liste des étudiants"""
        list_frame = tk.Frame(self.root, bg='white', relief=tk.RAISED, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('matricule', 'nom', 'faculte', 'promotion', 'email', 'telephone', 'statut')
        self.students_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # Configuration colonnes
        column_widths = {
            'matricule': 120,
            'nom': 200,
            'faculte': 180,
            'promotion': 100,
            'email': 180,
            'telephone': 120,
            'statut': 80
        }
        
        column_headers = {
            'matricule': 'Matricule',
            'nom': 'Nom Complet',
            'faculte': 'Faculté',
            'promotion': 'Promotion',
            'email': 'Email',
            'telephone': 'Téléphone',
            'statut': 'Statut'
        }
        
        for col in columns:
            self.students_tree.heading(col, text=column_headers[col])
            self.students_tree.column(col, width=column_widths[col])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.students_tree.xview)
        self.students_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement
        self.students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu contextuel
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="👁️ Voir détails", command=self.view_student)
        self.context_menu.add_command(label="✏️ Modifier", command=self.edit_student)
        self.context_menu.add_command(label="📸 Photos", command=self.manage_photos)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Supprimer", command=self.delete_student)
        
        # Bind events
        self.students_tree.bind("<Double-1>", lambda e: self.view_student())
        self.students_tree.bind("<Button-3>", self.show_context_menu)
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.root, bg='#f0f0f0', height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Statistiques
        stats_frame = tk.Frame(footer, bg='#f0f0f0')
        stats_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.total_count = tk.StringVar(value="0")
        self.active_count = tk.StringVar(value="0")
        
        stats_text = f"Total: {self.total_count.get()} | Actifs: {self.active_count.get()}"
        stats_label = tk.Label(stats_frame, text=stats_text, 
                               font=('Arial', 10), bg='#f0f0f0', fg='#666')
        stats_label.pack()
        
        # Bouton fermer
        close_btn = tk.Button(footer, text="Fermer", command=self.root.destroy,
                              bg='#6c757d', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def load_faculties(self):
        """Charger les facultés"""
        try:
            facultes = self.database.get_facultes()
            faculty_list = ['Toutes'] + [f['nom'] for f in facultes]
            self.faculty_combo['values'] = faculty_list
            self.faculty_combo.set('Toutes')
            
            # Charger les promotions
            promotions = self.database.get_promotions()
            promotion_list = ['Toutes'] + promotions
            self.promotion_combo['values'] = promotion_list
            self.promotion_combo.set('Toutes')
            
        except Exception as e:
            print(f"Erreur chargement facultés: {e}")
    
    def load_students(self):
        """Charger les étudiants"""
        try:
            # Effacer la liste actuelle
            for item in self.students_tree.get_children():
                self.students_tree.delete(item)
            
            # Obtenir les filtres
            faculty_filter = self.faculty_filter.get()
            promotion_filter = self.promotion_filter.get()
            search_term = self.search_var.get()
            
            # Convertir les filtres
            faculty_id = None
            if faculty_filter != 'Toutes':
                facultes = self.database.get_facultes()
                for f in facultes:
                    # f est un sqlite3.Row, accéder par index
                    if f[1] == faculty_filter:  # f[1] est le nom de la faculté
                        faculty_id = f[0]  # f[0] est l'ID
                        break
            
            promotion = None if promotion_filter == 'Toutes' else promotion_filter
            
            # Obtenir les étudiants
            students = self.database.get_students(faculty_id, promotion, search_term)
            
            # Insérer dans le treeview
            for student in students:
                # student est un sqlite3.Row, accéder par index
                # Ordre des colonnes: id, matricule, nom, postnom, prenom, email, telephone, faculte_id, promotion, statut, faculte_nom
                nom_complet = f"{student[2] or ''} {student[3] or ''} {student[4] or ''}".strip()  # nom, postnom, prenom
                
                self.students_tree.insert('', 'end', values=(
                    student[1],  # matricule
                    nom_complet,
                    student[10] if len(student) > 10 else '',  # faculte_nom
                    student[8] if len(student) > 8 else '',   # promotion
                    student[5] if len(student) > 5 else '',   # email
                    student[6] if len(student) > 6 else '',   # telephone
                    student[9] if len(student) > 9 else ''    # statut
                ))
            
            # Mettre à jour les statistiques
            self.update_statistics(students)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement étudiants: {str(e)}")
    
    def update_statistics(self, students):
        """Mettre à jour les statistiques"""
        total = len(students)
        active = len([s for s in students if len(s) > 9 and s[9] == 'actif'])  # s[9] est le statut
        
        self.total_count.set(str(total))
        self.active_count.set(str(active))
    
    def filter_students(self, *args):
        """Filtrer les étudiants"""
        self.load_students()
    
    def show_context_menu(self, event):
        """Afficher le menu contextuel"""
        item = self.students_tree.identify('item', event.x, event.y)
        if item:
            self.students_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def get_selected_student(self):
        """Obtenir l'étudiant sélectionné"""
        selected = self.students_tree.selection()
        if not selected:
            return None
        
        item = self.students_tree.item(selected[0])
        values = item['values']
        
        return {
            'matricule': values[0],
            'nom': values[1],
            'faculte': values[2],
            'promotion': values[3],
            'email': values[4],
            'telephone': values[5],
            'statut': values[6]
        }
    
    def view_student(self):
        """Voir les détails d'un étudiant"""
        student = self.get_selected_student()
        if not student:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un étudiant")
            return
        
        # Ouvrir la fenêtre de détails
        StudentDetailsWindow(self.root, student, self.database, view_only=True)
    
    def edit_student(self):
        """Modifier un étudiant"""
        student = self.get_selected_student()
        if not student:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un étudiant")
            return
        
        # Ouvrir la fenêtre d'édition
        StudentDetailsWindow(self.root, student, self.database, view_only=False)
    
    def manage_photos(self):
        """Gérer les photos d'un étudiant"""
        student = self.get_selected_student()
        if not student:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un étudiant")
            return
        
        messagebox.showinfo("Photos", f"Gestion photos pour {student['nom']}")
    
    def delete_student(self):
        """Supprimer un étudiant"""
        student = self.get_selected_student()
        if not student:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un étudiant")
            return
        
        # Extraire le nom complet depuis values[1]
        student_name = student['nom']  # values[1] contient le nom complet
        
        if messagebox.askyesno("Confirmation", 
                               f"Voulez-vous vraiment supprimer {student_name} ?\n"
                               "Cette action est irréversible."):
            # TODO: Implémenter la suppression dans la base de données
            messagebox.showinfo("Information", "Suppression en développement")
    
    def add_student(self):
        """Ajouter un nouvel étudiant"""
        StudentDetailsWindow(self.root, None, self.database, view_only=False, refresh_callback=self.load_students)
    
    def import_students(self):
        """Importer des étudiants"""
        messagebox.showinfo("Import", "Importation en développement")
    
    def export_students(self):
        """Exporter des étudiants"""
        messagebox.showinfo("Export", "Exportation en développement")

class StudentDetailsWindow:
    """Fenêtre de détails/édition d'étudiant"""
    
    def __init__(self, parent, student_data, database, view_only=False, refresh_callback=None):
        self.parent = parent
        self.student_data = student_data
        self.database = database
        self.view_only = view_only
        self.refresh_callback = refresh_callback
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("Détails Étudiant" if view_only else "Modifier Étudiant")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.matricule = tk.StringVar(value=student_data['matricule'] if student_data else '')
        self.nom = tk.StringVar(value=student_data['nom'] if student_data else '')
        self.postnom = tk.StringVar()
        self.prenom = tk.StringVar()
        self.email = tk.StringVar(value=student_data['email'] if student_data else '')
        self.telephone = tk.StringVar(value=student_data['telephone'] if student_data else '')
        self.faculte = tk.StringVar()
        self.promotion = tk.StringVar()
        self.statut = tk.StringVar(value='actif')
        
        # Photos
        self.student_photos = []
        self.photo_count = 0
        self.photo_status = tk.StringVar(value="Aucune photo")
        self.current_student_id = None
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données si édition
        if student_data:
            self.load_student_details()
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Formulaire
        form_frame = tk.Frame(self.window, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Champs du formulaire
        fields = [
            ("Matricule *:", self.matricule, False),
            ("Nom *:", self.nom, False),
            ("Postnom:", self.postnom, False),
            ("Prénom:", self.prenom, False),
            ("Email:", self.email, False),
            ("Téléphone:", self.telephone, False),
        ]
        
        for i, (label, var, readonly) in enumerate(fields):
            tk.Label(form_frame, text=label, font=('Arial', 11), bg='white').grid(
                row=i, column=0, sticky='w', pady=5, padx=(0, 10))
            
            # Cas spécial pour le matricule avec bouton auto-générer
            if label == "Matricule *:":
                matricule_frame = tk.Frame(form_frame, bg='white')
                matricule_frame.grid(row=i, column=1, sticky='ew', pady=5)
                
                entry = ttk.Entry(matricule_frame, textvariable=var, font=('Arial', 11), width=20)
                entry.pack(side=tk.LEFT)
                
                auto_btn = tk.Button(matricule_frame, text="🔄 Auto", 
                                   command=self.generate_and_set_matricule, bg='#ffc107', fg='white',
                                   font=('Arial', 9), relief=tk.FLAT, cursor='hand2')
                auto_btn.pack(side=tk.LEFT, padx=(5, 0))
            else:
                entry = ttk.Entry(form_frame, textvariable=var, font=('Arial', 11))
                if readonly:
                    entry.configure(state='readonly')
                entry.grid(row=i, column=1, sticky='ew', pady=5)
        
        # Faculté et promotion
        tk.Label(form_frame, text="Faculté:", font=('Arial', 11), bg='white').grid(
            row=6, column=0, sticky='w', pady=5, padx=(0, 10))
        
        self.faculty_combo = ttk.Combobox(form_frame, textvariable=self.faculte,
                                         font=('Arial', 11), state='readonly')
        self.faculty_combo.grid(row=6, column=1, sticky='ew', pady=5)
        
        tk.Label(form_frame, text="Promotion:", font=('Arial', 11), bg='white').grid(
            row=7, column=0, sticky='w', pady=5, padx=(0, 10))
        
        self.promotion_combo = ttk.Combobox(form_frame, textvariable=self.promotion,
                                           font=('Arial', 11), state='readonly')
        self.promotion_combo.grid(row=7, column=1, sticky='ew', pady=5)
        
        # Statut
        tk.Label(form_frame, text="Statut:", font=('Arial', 11), bg='white').grid(
            row=8, column=0, sticky='w', pady=5, padx=(0, 10))
        
        status_combo = ttk.Combobox(form_frame, textvariable=self.statut,
                                   values=['actif', 'inactif', 'diplômé'],
                                   font=('Arial', 11), state='readonly')
        status_combo.grid(row=8, column=1, sticky='ew', pady=5)
        
        # Configuration grid
        form_frame.columnconfigure(1, weight=1)
        
        # Photos
        photo_frame = tk.LabelFrame(form_frame, text="Photos de l'étudiant", 
                                  font=('Arial', 11, 'bold'), bg='white')
        photo_frame.grid(row=9, column=0, columnspan=2, sticky='ew', pady=20)
        
        # Statut photos
        self.photo_status = tk.StringVar(value="Aucune photo")
        status_label = tk.Label(photo_frame, textvariable=self.photo_status, 
                               font=('Arial', 10), bg='white', fg='#666')
        status_label.pack(pady=5)
        
        # Boutons photo
        photo_buttons_frame = tk.Frame(photo_frame, bg='white')
        photo_buttons_frame.pack(pady=10)
        
        capture_btn = tk.Button(photo_buttons_frame, text="📸 Capturer 5 photos", 
                               command=self.capture_photos, bg='#17a2b8', fg='white',
                               font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        capture_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = tk.Button(photo_buttons_frame, text="📁 Importer photos", 
                              command=self.import_photos, bg='#6f42c1', fg='white',
                              font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        import_btn.pack(side=tk.LEFT, padx=5)
        
        view_btn = tk.Button(photo_buttons_frame, text="👁️ Voir photos", 
                            command=self.view_photos, bg='#28a745', fg='white',
                            font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        view_btn.pack(side=tk.LEFT, padx=5)
        
        # Boutons
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        if not self.view_only:
            save_btn = tk.Button(button_frame, text="💾 Enregistrer", command=self.save_student,
                               bg='#28a745', fg='white', font=('Arial', 11, 'bold'),
                               relief=tk.FLAT, cursor='hand2')
            save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="❌ Annuler", command=self.window.destroy,
                              bg='#dc3545', fg='white', font=('Arial', 11),
                              relief=tk.FLAT, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Charger les facultés et promotions
        self.load_dropdowns()
    
    def load_dropdowns(self):
        """Charger les dropdowns"""
        try:
            # Facultés
            facultes = self.database.get_facultes()
            faculty_list = [f['nom'] for f in facultes]
            self.faculty_combo['values'] = faculty_list
            
            # Promotions
            promotions = self.database.get_promotions()
            self.promotion_combo['values'] = promotions
            
        except Exception as e:
            print(f"Erreur chargement dropdowns: {e}")
    
    def load_student_details(self):
        """Charger les détails de l'étudiant"""
        # TODO: Charger les détails complets depuis la base de données
        pass
    
    def manage_photos(self):
        """Gérer les photos"""
        messagebox.showinfo("Photos", "Gestion photos en développement")
    
    def capture_photos(self):
        """Capturer 5 photos avec la caméra"""
        from views.photo_capture import PhotoCaptureWindow
        PhotoCaptureWindow(self.window, self)
    
    def import_photos(self):
        """Importer des photos depuis des fichiers"""
        from tkinter import filedialog
        import os
        from PIL import Image
        
        files = filedialog.askopenfilenames(
            title="Sélectionner 5 photos de l'étudiant",
            filetypes=[("Images", "*.jpg *.jpeg *.png"), ("Tous les fichiers", "*.*")]
        )
        
        if len(files) != 5:
            messagebox.showwarning("Attention", "Veuillez sélectionner exactement 5 photos")
            return
        
        self.student_photos = []
        for i, file_path in enumerate(files):
            try:
                # Vérifier et redimensionner l'image
                img = Image.open(file_path)
                if img.size != (224, 224):
                    img = img.resize((224, 224), Image.Resampling.LANCZOS)
                
                # Sauvegarder dans Dataset
                student_name = self.generate_student_name()
                photo_filename = f"Dataset/{student_name}_{i+1}.jpg"
                img.save(photo_filename)
                self.student_photos.append(photo_filename)
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur traitement photo {i+1}: {str(e)}")
                return
        
        self.photo_count = len(self.student_photos)
        self.photo_status.set(f"{self.photo_count} photos importées")
        messagebox.showinfo("Succès", "Photos importées avec succès")
    
    def view_photos(self):
        """Voir les photos capturées"""
        if not self.student_photos:
            messagebox.showinfo("Photos", "Aucune photo à afficher")
            return
        
        from views.photo_capture import PhotoViewWindow
        PhotoViewWindow(self.window, self.student_photos)
    
    def generate_student_name(self):
        """Générer un nom pour les fichiers photos"""
        nom = self.nom.get().strip().replace(" ", "_")
        postnom = self.postnom.get().strip().replace(" ", "_")
        prenom = self.prenom.get().strip().replace(" ", "_")
        
        student_name = f"{nom}_{postnom}_{prenom}".replace("__", "_").strip("_")
        
        # Nettoyer les caractères spéciaux
        import re
        student_name = re.sub(r'[^a-zA-Z0-9_]', '', student_name)
        
        if not student_name:
            student_name = f"student_{self.current_student_id or 'new'}"
        
        return student_name
    
    def save_student(self):
        """Sauvegarder l'étudiant"""
        # Validation
        matricule = self.matricule.get().strip()
        nom = self.nom.get().strip()
        
        if not matricule or not nom:
            messagebox.showerror("Erreur", "Matricule et nom sont obligatoires")
            return
        
        if not self.student_photos:
            messagebox.showerror("Erreur", "Veuillez capturer ou importer au moins une photo")
            return
        
        try:
            # Sauvegarder dans la base de données
            student_id, generated_matricule = self.database.add_student(
                nom=nom,
                postnom=self.postnom.get().strip(),
                prenom=self.prenom.get().strip(),
                faculte_id=self.get_faculty_id(),
                promotion=self.promotion.get().strip(),
                email=self.email.get().strip(),
                telephone=self.telephone.get().strip()
            )
            
            # Mettre à jour le matricule avec celui généré par la base
            self.matricule.set(generated_matricule)
            
            messagebox.showinfo("Succès", f"Étudiant {nom} enregistré avec {len(self.student_photos)} photos")
            
            # Rafraîchir la liste des étudiants
            if self.refresh_callback:
                self.refresh_callback()
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde: {str(e)}")
    
    def generate_and_set_matricule(self):
        """Générer et définir le matricule automatiquement"""
        matricule = self.generate_matricule()
        self.matricule.set(matricule)
    
    def generate_matricule(self):
        """Générer un matricule automatique"""
        import datetime
        year = datetime.datetime.now().year
        faculty_id = self.get_faculty_id()
        
        # TODO: Compter le nombre d'étudiants pour générer un ID unique
        student_count = 1  # Remplacer par un vrai compteur
        
        return f"UCC-{year}-{faculty_id}-{student_count:04d}"
    
    def get_faculty_id(self):
        """Obtenir l'ID de la faculté sélectionnée"""
        facultes = self.database.get_facultes()
        faculty_name = self.faculte.get()
        
        for faculte in facultes:
            if faculte[1] == faculty_name:  # faculte[1] est le nom
                return faculte[0]  # faculte[0] est l'ID
        
        return 1  # Valeur par défaut

def main():
    """Test du module étudiants"""
    root = tk.Tk()
    
    # Données test
    from database.database import DatabaseUCC
    database = DatabaseUCC()
    
    user_data = {
        'id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    app = StudentsScreen(root, user_data, database)
    root.mainloop()

if __name__ == "__main__":
    main()
