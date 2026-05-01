"""
Portail Principal - Dashboard Système UCC
Interface principale avec raccourcis vers les modules
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

class PortalScreen:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Portail UCC - {user_data['nom_complet']}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Import des modules
        from database.database import DatabaseUCC
        self.database = DatabaseUCC()
        
        # Variables
        self.current_time = tk.StringVar()
        self.user_info = tk.StringVar()
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer l'horloge
        self.update_clock()
        
        # Charger les statistiques
        self.load_statistics()
        
        # Démarrer le rafraîchissement automatique
        self.auto_refresh_statistics()
        
        # Gérer la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configurer l'interface du portail"""
        
        # Header
        self.create_header()
        
        # Contenu principal
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar gauche
        self.create_sidebar(main_container)
        
        # Zone principale avec raccourcis
        self.create_main_content(main_container)
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.root, bg='#003366', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo et titre
        left_frame = tk.Frame(header, bg='#003366')
        left_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        logo_label = tk.Label(left_frame, text="🎓 UCC", 
                              font=('Arial', 24, 'bold'), bg='#003366', fg='white')
        logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(left_frame, text="Système de Pointage", 
                              font=('Arial', 16), bg='#003366', fg='#E6F2FF')
        title_label.pack(side=tk.LEFT)
        
        # Infos utilisateur et heure
        right_frame = tk.Frame(header, bg='#003366')
        right_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Heure
        time_label = tk.Label(right_frame, textvariable=self.current_time, 
                             font=('Arial', 12), bg='#003366', fg='white')
        time_label.pack(anchor='e')
        
        # Utilisateur
        user_label = tk.Label(right_frame, textvariable=self.user_info, 
                             font=('Arial', 11, 'bold'), bg='#003366', fg='#E6F2FF')
        user_label.pack(anchor='e')
        
        # Bouton déconnexion
        logout_btn = tk.Button(right_frame, text="🚪 Déconnexion", 
                              command=self.logout, bg='#dc3545', fg='white',
                              font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        logout_btn.pack(anchor='e', pady=(10, 0))
        
        # Mettre à jour les infos utilisateur
        self.user_info.set(f"{self.user_data['nom_complet']} ({self.user_data['role'].title()})")
    
    def create_sidebar(self, parent):
        """Créer la barre latérale"""
        sidebar = tk.Frame(parent, bg='white', width=250, relief=tk.RAISED, borderwidth=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Titre sidebar
        sidebar_title = tk.Label(sidebar, text="MENU PRINCIPAL", 
                                font=('Arial', 14, 'bold'), bg='white', fg='#003366')
        sidebar_title.pack(pady=20)
        
        # Séparateur
        separator1 = ttk.Separator(sidebar, orient='horizontal')
        separator1.pack(fill=tk.X, padx=20, pady=10)
        
        # Menu items
        menu_items = [
            ("🏠 Tableau de bord", self.show_dashboard, "#007bff"),
            ("👥 Gestion étudiants", self.open_students, "#28a745"),
            ("📸 Pointage (Caméra)", self.open_attendance, "#ffc107"),
            ("🏛️ Organisation", self.open_organization, "#17a2b8"),
            ("📊 Rapports", self.open_reports, "#6f42c1"),
            ("⚙️ Paramètres", self.open_settings, "#6c757d"),
        ]
        
        for text, command, color in menu_items:
            btn_frame = tk.Frame(sidebar, bg='white')
            btn_frame.pack(fill=tk.X, padx=10, pady=2)
            
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 11),
                           relief=tk.FLAT, cursor='hand2', anchor='w')
            btn.pack(fill=tk.X, pady=2)
        
        # Séparateur
        separator2 = ttk.Separator(sidebar, orient='horizontal')
        separator2.pack(fill=tk.X, padx=20, pady=20)
        
        # Statistiques rapides
        stats_title = tk.Label(sidebar, text="STATISTIQUES", 
                              font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        stats_title.pack(pady=(0, 10))
        
        # Variables statistiques
        self.total_students_var = tk.StringVar(value="0")
        self.present_today_var = tk.StringVar(value="0")
        self.attendance_rate_var = tk.StringVar(value="0%")
        self.absent_today_var = tk.StringVar(value="0")
        self.late_arrivals_var = tk.StringVar(value="0")
        self.early_departures_var = tk.StringVar(value="0")
        self.last_update_var = tk.StringVar(value="Dernière mise à jour: --:--:--")
        
        stats = [
            ("Total Étudiants:", self.total_students_var),
            ("Présents Aujourd'hui:", self.present_today_var),
            ("Absents Aujourd'hui:", self.absent_today_var),
            ("Taux Présence:", self.attendance_rate_var),
            ("Arrivées Tardives:", self.late_arrivals_var),
            ("Départs Anticipés:", self.early_departures_var),
        ]
        
        for label_text, var in stats:
            stat_frame = tk.Frame(sidebar, bg='white')
            stat_frame.pack(fill=tk.X, padx=20, pady=5)
            
            label = tk.Label(stat_frame, text=label_text, font=('Arial', 10), 
                           bg='white', fg='#666', anchor='w')
            label.pack(fill=tk.X)
            
            value = tk.Label(stat_frame, textvariable=var, font=('Arial', 12, 'bold'), 
                           bg='white', fg='#003366', anchor='w')
            value.pack(fill=tk.X)
        
        # Heure de dernière mise à jour
        update_frame = tk.Frame(sidebar, bg='white')
        update_frame.pack(fill=tk.X, padx=20, pady=(20, 5))
        
        update_label = tk.Label(update_frame, textvariable=self.last_update_var, 
                               font=('Arial', 8), bg='white', fg='#999', anchor='w')
        update_label.pack(fill=tk.X)
    
    def create_main_content(self, parent):
        """Créer la zone principale avec raccourcis"""
        main_content = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Titre
        title_frame = tk.Frame(main_content, bg='#E6F2FF')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="TABLEAU DE BORD - RACCOURCIS", 
                               font=('Arial', 18, 'bold'), bg='#E6F2FF', fg='#003366')
        title_label.pack(pady=20)
        
        # Grid des raccourcis
        shortcuts_frame = tk.Frame(main_content, bg='white')
        shortcuts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configuration du grid
        for i in range(3):
            shortcuts_frame.columnconfigure(i, weight=1, uniform='cell')
        for i in range(2):
            shortcuts_frame.rowconfigure(i, weight=1, uniform='cell')
        
        # Raccourcis principaux
        shortcuts = [
            {
                'title': '👥 GESTION ÉTUDIANTS',
                'desc': 'Ajouter, modifier, supprimer\nles étudiants',
                'color': '#28a745',
                'command': self.open_students,
                'row': 0, 'col': 0
            },
            {
                'title': '📸 POINTAGE',
                'desc': 'Caméra de reconnaissance\nfaciale en direct',
                'color': '#ffc107',
                'command': self.open_attendance,
                'row': 0, 'col': 1
            },
            {
                'title': '🏛️ ORGANISATION',
                'desc': 'Facultés et promotions\nconfiguration',
                'color': '#17a2b8',
                'command': self.open_organization,
                'row': 0, 'col': 2
            },
            {
                'title': '📊 RAPPORTS',
                'desc': 'Génération de rapports\net statistiques',
                'color': '#6f42c1',
                'command': self.open_reports,
                'row': 1, 'col': 0
            },
            {
                'title': '⚙️ PARAMÈTRES',
                'desc': 'Configuration du\nsystème',
                'color': '#6c757d',
                'command': self.open_settings,
                'row': 1, 'col': 1
            },
            {
                'title': '📈 STATISTIQUES',
                'desc': 'Vue détaillée des\nstatistiques',
                'color': '#007bff',
                'command': self.show_dashboard,
                'row': 1, 'col': 2
            }
        ]
        
        for shortcut in shortcuts:
            self.create_shortcut_card(shortcuts_frame, shortcut)
    
    def create_shortcut_card(self, parent, shortcut):
        """Créer une carte de raccourci"""
        card_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=2)
        card_frame.grid(row=shortcut['row'], column=shortcut['col'], 
                       padx=10, pady=10, sticky='nsew')
        
        # Header de la carte
        header_frame = tk.Frame(card_frame, bg=shortcut['color'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Icône et titre
        icon_label = tk.Label(header_frame, text=shortcut['title'], 
                              font=('Arial', 14, 'bold'), 
                              bg=shortcut['color'], fg='white')
        icon_label.pack(pady=25)
        
        # Description
        desc_label = tk.Label(card_frame, text=shortcut['desc'], 
                              font=('Arial', 10), bg='white', fg='#666',
                              justify=tk.CENTER)
        desc_label.pack(pady=20, padx=10)
        
        # Bouton
        btn_frame = tk.Frame(card_frame, bg='white')
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 20))
        
        btn = tk.Button(btn_frame, text="OUVRIR", command=shortcut['command'],
                        bg=shortcut['color'], fg='white', font=('Arial', 10, 'bold'),
                        relief=tk.FLAT, cursor='hand2')
        btn.pack(fill=tk.X)
        
        # Hover effect
        def on_enter(e):
            btn.config(bg=self.darken_color(shortcut['color']))
        
        def on_leave(e):
            btn.config(bg=shortcut['color'])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def darken_color(self, color):
        """Assombrir une couleur pour l'effet hover"""
        colors = {
            '#28a745': '#218838',
            '#ffc107': '#e0a800',
            '#17a2b8': '#138496',
            '#6f42c1': '#59359a',
            '#6c757d': '#545b62',
            '#007bff': '#0056b3'
        }
        return colors.get(color, color)
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.root, bg='#003366', height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_text = tk.Label(footer, text="© 2024 Université Catholique du Congo - Système de Pointage", 
                               font=('Arial', 9), bg='#003366', fg='white')
        footer_text.pack(pady=5)
    
    def update_clock(self):
        """Mettre à jour l'horloge"""
        now = datetime.now()
        self.current_time.set(now.strftime("%d/%m/%Y %H:%M:%S"))
        self.root.after(1000, self.update_clock)
    
    def load_statistics(self):
        """Charger les statistiques"""
        try:
            stats = self.database.get_statistics()
            self.total_students_var.set(str(stats.get('total_students', 0)))
            self.present_today_var.set(str(stats.get('present_today', 0)))
            self.attendance_rate_var.set(f"{stats.get('attendance_rate', 0):.1f}%")
            
            # Ajouter des statistiques supplémentaires
            self.absent_today_var.set(str(stats.get('absent_today', 0)))
            self.late_arrivals_var.set(str(stats.get('late_arrivals', 0)))
            self.early_departures_var.set(str(stats.get('early_departures', 0)))
            
            # Mettre à jour l'heure de dernière mise à jour
            self.last_update_var.set(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"Erreur chargement statistiques: {e}")
            # Valeurs par défaut en cas d'erreur
            self.total_students_var.set("0")
            self.present_today_var.set("0")
            self.attendance_rate_var.set("0%")
            self.absent_today_var.set("0")
            self.late_arrivals_var.set("0")
            self.early_departures_var.set("0")
    
    def auto_refresh_statistics(self):
        """Rafraîchissement automatique des statistiques"""
        self.load_statistics()
        # Planifier le prochain rafraîchissement (toutes les 30 secondes)
        self.root.after(30000, self.auto_refresh_statistics)
    
    # Actions des modules
    def show_dashboard(self):
        """Afficher le dashboard détaillé"""
        from views.dashboard import DashboardScreen
        DashboardScreen(self.root, self.user_data, self.database)
    
    def open_students(self):
        """Ouvrir le module gestion étudiants"""
        from views.students import StudentsScreen
        students_window = tk.Toplevel(self.root)
        students_window.title("Gestion des Étudiants")
        app = StudentsScreen(students_window, self.user_data, self.database)
        try:
            students_window.transient(self.root)
            students_window.grab_set()
        except:
            pass  # Ignorer l'erreur transient
    
    def open_attendance(self):
        """Ouvrir le module de pointage"""
        from views.attendance import AttendanceScreen
        attendance_window = tk.Toplevel(self.root)
        attendance_window.title("Pointage - Reconnaissance Faciale")
        app = AttendanceScreen(attendance_window, self.user_data, self.database)
        try:
            attendance_window.transient(self.root)
            attendance_window.grab_set()
        except:
            pass  # Ignorer l'erreur transient
    
    def open_organization(self):
        """Ouvrir le module organisation"""
        from views.organization import OrganizationScreen
        org_window = tk.Toplevel(self.root)
        org_window.title("Organisation - Facultés et Promotions")
        app = OrganizationScreen(org_window, self.user_data, self.database)
        try:
            org_window.transient(self.root)
            org_window.grab_set()
        except:
            pass  # Ignorer l'erreur transient
    
    def open_reports(self):
        """Ouvrir le module rapports"""
        from views.reports import ReportsScreen
        ReportsScreen(self.root, self.user_data, self.database)
    
    def open_settings(self):
        """Ouvrir le module paramètres"""
        from views.settings import SettingsScreen
        SettingsScreen(self.root, self.user_data, self.database)
    
    def logout(self):
        """Déconnexion"""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            # Log de déconnexion
            self.database.log_action(self.user_data['id'], "LOGOUT", "Déconnexion utilisateur")
            
            # Fermer le portail
            self.root.destroy()
            
            # Réouvrir l'écran de connexion
            from views.login import LoginScreen
            login_root = tk.Tk()
            app = LoginScreen(login_root)
            login_root.mainloop()
    
    def on_closing(self):
        """Gérer la fermeture"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.database.log_action(self.user_data['id'], "EXIT", "Fermeture application")
            self.root.destroy()

def main():
    """Test du portail"""
    root = tk.Tk()
    
    # Données test utilisateur
    test_user = {
        'id': 1,
        'username': 'admin',
        'role': 'admin',
        'nom_complet': 'Administrateur UCC',
        'faculte_access': 'all'
    }
    
    app = PortalScreen(root, test_user)
    root.mainloop()

if __name__ == "__main__":
    main()
