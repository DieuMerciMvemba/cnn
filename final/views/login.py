"""
Écran de connexion - Système UCC
Login sécurisé avec authentification
"""

import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from database.database import DatabaseUCC

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Connexion - Système UCC")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Base de données
        self.database = DatabaseUCC()
        
        # Variables
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.remember_me = tk.BooleanVar()
        
        # Créer l'interface
        self.setup_ui()
        
        # Centrer la fenêtre
        self.center_window()
        
        # Focus sur username
        self.username_entry.focus()
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Configurer l'interface de connexion"""
        
        # Header avec logo UCC
        header_frame = tk.Frame(self.root, bg='#003366', height=100)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo et titre
        logo_label = tk.Label(header_frame, text="🎓", font=('Arial', 32), 
                            bg='#003366', fg='white')
        logo_label.pack(pady=(20, 5))
        
        title_label = tk.Label(header_frame, text="Université Catholique du Congo", 
                              font=('Arial', 14, 'bold'), bg='#003366', fg='white')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Système de Pointage par Reconnaissance Faciale", 
                                font=('Arial', 10), bg='#003366', fg='#E6F2FF')
        subtitle_label.pack(pady=(5, 20))
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='white', relief=tk.RAISED, borderwidth=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre connexion
        login_title = tk.Label(main_frame, text="CONNEXION", 
                              font=('Arial', 16, 'bold'), bg='white', fg='#003366')
        login_title.pack(pady=(30, 20))
        
        # Formulaire de connexion
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(pady=10)
        
        # Username
        username_label = tk.Label(form_frame, text="Nom d'utilisateur :", 
                                 font=('Arial', 11), bg='white', anchor='w')
        username_label.pack(fill=tk.X, pady=(0, 5))
        
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username, 
                                       font=('Arial', 11), width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Password
        password_label = tk.Label(form_frame, text="Mot de passe :", 
                                font=('Arial', 11), bg='white', anchor='w')
        password_label.pack(fill=tk.X, pady=(0, 5))
        
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password, 
                                       font=('Arial', 11), width=30, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Remember me
        remember_check = tk.Checkbutton(form_frame, text="Se souvenir de moi", 
                                       variable=self.remember_me, bg='white', 
                                       font=('Arial', 10))
        remember_check.pack(anchor='w', pady=(0, 20))
        
        # Boutons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(pady=20)
        
        login_button = tk.Button(button_frame, text="SE CONNECTER", 
                               command=self.login, bg='#003366', fg='white',
                               font=('Arial', 12, 'bold'), width=20, height=2,
                               cursor='hand2', relief=tk.FLAT)
        login_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="ANNULER", 
                                 command=self.cancel, bg='#6c757d', fg='white',
                                 font=('Arial', 12), width=20, height=2,
                                 cursor='hand2', relief=tk.FLAT)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Mot de passe oublié
        forgot_link = tk.Label(main_frame, text="Mot de passe oublié ?", 
                              font=('Arial', 10, 'underline'), bg='white', 
                              fg='#003366', cursor='hand2')
        forgot_link.pack(pady=10)
        forgot_link.bind("<Button-1>", self.forgot_password)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#f0f0f0')
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_text = tk.Label(footer_frame, text="© 2024 UCC - Tous droits réservés", 
                             font=('Arial', 9), bg='#f0f0f0', fg='#666')
        footer_text.pack(pady=10)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
    
    def hash_password(self, password):
        """Hasher le mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        """Authentifier l'utilisateur"""
        username = self.username.get().strip()
        password = self.password.get().strip()
        
        # Validation
        if not username:
            messagebox.showerror("Erreur", "Veuillez entrer votre nom d'utilisateur")
            self.username_entry.focus()
            return
        
        if not password:
            messagebox.showerror("Erreur", "Veuillez entrer votre mot de passe")
            self.password_entry.focus()
            return
        
        try:
            # Vérifier dans la base de données
            with self.database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, password_hash, role, nom_complet, faculte_access
                    FROM users WHERE username = ?
                ''', (username,))
                
                user = cursor.fetchone()
                
                if user and self.database.verify_password(password, user['password_hash']):
                    # Authentification réussie
                    self.login_success(user)
                else:
                    # Échec
                    messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")
                    self.password_entry.delete(0, tk.END)
                    self.password_entry.focus()
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de connexion: {str(e)}")
    
    def login_success(self, user):
        """Connexion réussie - ouvrir le portail"""
        # Log de connexion
        self.database.log_action(user['id'], "LOGIN", f"Connexion réussie: {user['username']}")
        
        # Fermer l'écran de connexion
        self.root.destroy()
        
        # Ouvrir le portail principal
        from views.portal import PortalScreen
        portal_root = tk.Tk()
        app = PortalScreen(portal_root, user)
        portal_root.mainloop()
    
    def cancel(self):
        """Annuler et quitter"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.root.destroy()
    
    def forgot_password(self, event):
        """Mot de passe oublié"""
        messagebox.showinfo("Mot de passe oublié", 
                           "Veuillez contacter l'administrateur système\n"
                           "Email: admin@ucc.edu\n"
                           "Tél: +243 123 456 789")

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
