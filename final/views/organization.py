"""
Module Organisation - Système UCC
Gestion des facultés et promotions
"""

import tkinter as tk
from tkinter import ttk, messagebox

class OrganizationScreen:
    def __init__(self, root, user_data, database):
        self.root = root
        self.user_data = user_data
        self.database = database
        
        # Configuration fenêtre
        self.root.geometry("900x600")
        self.root.configure(bg='#f0f0f0')
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données
        self.load_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        self.create_header()
        
        # Contenu principal avec onglets
        self.create_tabs()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.root, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(header, text="🏛️ ORGANISATION - FACULTÉS ET PROMOTIONS", 
                              font=('Arial', 18, 'bold'), bg='#003366', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Bouton fermer
        close_btn = tk.Button(header, text="Fermer", command=self.root.destroy,
                              bg='#6c757d', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def create_tabs(self):
        """Créer les onglets"""
        tab_frame = tk.Frame(self.root, bg='white')
        tab_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer les onglets
        self.notebook = ttk.Notebook(tab_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet Facultés
        self.create_faculties_tab()
        
        # Onglet Promotions
        self.create_promotions_tab()
    
    def create_faculties_tab(self):
        """Créer l'onglet Facultés"""
        faculties_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(faculties_frame, text="🏛️ Facultés")
        
        # Header de l'onglet
        header_frame = tk.Frame(faculties_frame, bg='#E6F2FF')
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        title_label = tk.Label(header_frame, text="GESTION DES FACULTÉS", 
                               font=('Arial', 16, 'bold'), bg='#E6F2FF', fg='#003366')
        title_label.pack(pady=10)
        
        # Boutons d'action
        actions_frame = tk.Frame(faculties_frame, bg='white')
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        add_btn = tk.Button(actions_frame, text="+ Ajouter une faculté", 
                           command=self.add_faculty, bg='#28a745', fg='white',
                           font=('Arial', 10, 'bold'), relief=tk.FLAT, cursor='hand2')
        add_btn.pack(side=tk.LEFT)
        
        # Liste des facultés
        list_frame = tk.Frame(faculties_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('id', 'nom', 'description', 'created_at')
        self.faculties_tree = ttk.Treeview(list_frame, columns=columns, 
                                          show='headings', height=15)
        
        # Configuration colonnes
        self.faculties_tree.heading('id', text='ID')
        self.faculties_tree.heading('nom', text='Nom de la Faculté')
        self.faculties_tree.heading('description', text='Description')
        self.faculties_tree.heading('created_at', text='Date de Création')
        
        self.faculties_tree.column('id', width=50)
        self.faculties_tree.column('nom', width=250)
        self.faculties_tree.column('description', width=300)
        self.faculties_tree.column('created_at', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.faculties_tree.yview)
        self.faculties_tree.configure(yscrollcommand=scrollbar.set)
        
        self.faculties_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Menu contextuel
        self.faculties_context_menu = tk.Menu(self.root, tearoff=0)
        self.faculties_context_menu.add_command(label="✏️ Modifier", command=self.edit_faculty)
        self.faculties_context_menu.add_command(label="🗑️ Supprimer", command=self.delete_faculty)
        
        self.faculties_tree.bind("<Button-3>", self.show_faculties_context_menu)
    
    def create_promotions_tab(self):
        """Créer l'onglet Promotions"""
        promotions_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(promotions_frame, text="📚 Promotions")
        
        # Header de l'onglet
        header_frame = tk.Frame(promotions_frame, bg='#E6F2FF')
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        title_label = tk.Label(header_frame, text="GESTION DES PROMOTIONS", 
                               font=('Arial', 16, 'bold'), bg='#E6F2FF', fg='#003366')
        title_label.pack(pady=10)
        
        # Information
        info_frame = tk.Frame(promotions_frame, bg='#E6F2FF')
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        info_text = ("Les promotions sont prédéfinies dans le système UCC. "
                    "Elles suivent la structure académique standard.")
        
        info_label = tk.Label(info_frame, text=info_text, font=('Arial', 11), 
                              bg='#E6F2FF', fg='#003366', justify=tk.LEFT)
        info_label.pack(pady=10, padx=20)
        
        # Liste des promotions
        list_frame = tk.Frame(promotions_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ('promotion', 'description', 'ordre')
        self.promotions_tree = ttk.Treeview(list_frame, columns=columns, 
                                           show='headings', height=15)
        
        # Configuration colonnes
        self.promotions_tree.heading('promotion', text='Promotion')
        self.promotions_tree.heading('description', text='Description')
        self.promotions_tree.heading('ordre', text='Ordre')
        
        self.promotions_tree.column('promotion', width=150)
        self.promotions_tree.column('description', width=400)
        self.promotions_tree.column('ordre', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.promotions_tree.yview)
        self.promotions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.promotions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.root, bg='#f0f0f0', height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_text = tk.Label(footer, text="© 2024 UCC - Module Organisation", 
                               font=('Arial', 9), bg='#f0f0f0', fg='#666')
        footer_text.pack(pady=10)
    
    def load_data(self):
        """Charger les données"""
        self.load_faculties()
        self.load_promotions()
    
    def load_faculties(self):
        """Charger les facultés"""
        try:
            # Effacer la liste actuelle
            for item in self.faculties_tree.get_children():
                self.faculties_tree.delete(item)
            
            # Obtenir les facultés
            facultes = self.database.get_facultes()
            
            # Insérer dans le treeview
            for faculte in facultes:
                # Convertir sqlite3.Row en tuple
                if hasattr(faculte, 'keys'):
                    # C'est un Row object
                    values = tuple(faculte)
                else:
                    # C'est déjà un tuple
                    values = faculte
                
                # Ajouter les valeurs avec des valeurs par défaut
                self.faculties_tree.insert('', 'end', values=(
                    values[0] if len(values) > 0 else '',  # id
                    values[1] if len(values) > 1 else '',  # nom
                    values[2] if len(values) > 2 else '',  # description
                    values[3] if len(values) > 3 else ''   # created_at
                ))
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement facultés: {str(e)}")
    
    def load_promotions(self):
        """Charger les promotions"""
        try:
            # Effacer la liste actuelle
            for item in self.promotions_tree.get_children():
                self.promotions_tree.delete(item)
            
            # Promotions prédéfinies
            promotions = [
                ("LICENCE 1", "Première année de Licence", 1),
                ("LICENCE 2", "Deuxième année de Licence", 2),
                ("LICENCE 3", "Troisième année de Licence", 3),
                ("MASTER 1", "Première année de Master", 4),
                ("MASTER 2", "Deuxième année de Master", 5)
            ]
            
            # Insérer dans le treeview
            for promotion, description, ordre in promotions:
                self.promotions_tree.insert('', 'end', values=(
                    promotion, description, ordre
                ))
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement promotions: {str(e)}")
    
    def show_faculties_context_menu(self, event):
        """Afficher le menu contextuel des facultés"""
        item = self.faculties_tree.identify('item', event.x, event.y)
        if item:
            self.faculties_tree.selection_set(item)
            self.faculties_context_menu.post(event.x_root, event.y_root)
    
    def add_faculty(self):
        """Ajouter une faculté"""
        FacultyDialog(self.root, self.database, self.load_faculties)
    
    def edit_faculty(self):
        """Modifier une faculté"""
        selected = self.faculties_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une faculté")
            return
        
        item = self.faculties_tree.item(selected[0])
        faculty_id = item['values'][0]
        
        FacultyDialog(self.root, self.database, self.load_faculties, faculty_id)
    
    def delete_faculty(self):
        """Supprimer une faculté"""
        selected = self.faculties_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une faculté")
            return
        
        item = self.faculties_tree.item(selected[0])
        faculty_name = item['values'][1]
        
        if messagebox.askyesno("Confirmation", 
                               f"Voulez-vous vraiment supprimer la faculté '{faculty_name}' ?"):
            # TODO: Implémenter la suppression
            messagebox.showinfo("Information", "Suppression en développement")

class FacultyDialog:
    """Boîte de dialogue pour ajouter/modifier une faculté"""
    
    def __init__(self, parent, database, refresh_callback, faculty_id=None):
        self.parent = parent
        self.database = database
        self.refresh_callback = refresh_callback
        self.faculty_id = faculty_id
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("Ajouter une Faculté" if not faculty_id else "Modifier une Faculté")
        self.window.geometry("400x250")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.name_var = tk.StringVar()
        self.description_text = None
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données si édition
        if faculty_id:
            self.load_faculty_data()
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Formulaire
        form_frame = tk.Frame(self.window, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Nom de la faculté
        tk.Label(form_frame, text="Nom de la faculté:", font=('Arial', 11), 
                bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, 
                               font=('Arial', 11), width=40)
        name_entry.grid(row=0, column=1, sticky='ew', pady=10)
        
        # Description
        tk.Label(form_frame, text="Description:", font=('Arial', 11), 
                bg='white').grid(row=1, column=0, sticky='nw', pady=10)
        
        self.description_text = tk.Text(form_frame, font=('Arial', 11), width=40, height=5)
        self.description_text.grid(row=1, column=1, sticky='ew', pady=10)
        
        # Configuration grid
        form_frame.columnconfigure(1, weight=1)
        
        # Boutons
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(button_frame, text="💾 Enregistrer", command=self.save,
                           bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                           relief=tk.FLAT, cursor='hand2')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="❌ Annuler", command=self.window.destroy,
                              bg='#dc3545', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def load_faculty_data(self):
        """Charger les données de la faculté"""
        # TODO: Charger depuis la base de données
        pass
    
    def save(self):
        """Sauvegarder la faculté"""
        name = self.name_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip() if self.description_text else ""
        
        if not name:
            messagebox.showerror("Erreur", "Veuillez entrer le nom de la faculté")
            return
        
        try:
            # TODO: Sauvegarder dans la base de données
            messagebox.showinfo("Succès", "Faculté sauvegardée avec succès")
            self.refresh_callback()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde: {str(e)}")

def main():
    """Test du module organisation"""
    root = tk.Tk()
    
    # Données test
    from database.database import DatabaseUCC
    database = DatabaseUCC()
    
    user_data = {
        'id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    app = OrganizationScreen(root, user_data, database)
    root.mainloop()

if __name__ == "__main__":
    main()
