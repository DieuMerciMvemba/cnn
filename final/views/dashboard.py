"""
Dashboard Détaillé - Système UCC
Interface avec graphiques et statistiques avancées
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class DashboardScreen:
    def __init__(self, parent, user_data, database):
        self.parent = parent
        self.user_data = user_data
        self.database = database
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("📈 Tableau de Bord Détaillé")
        self.window.geometry("1200x800")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.selected_period = tk.StringVar(value="7jours")
        self.selected_faculty = tk.StringVar(value="Toutes")
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données
        self.refresh_data()
        
        # Gérer la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configurer l'interface du dashboard"""
        
        # Header
        self.create_header()
        
        # Filtres
        self.create_filters()
        
        # Zone principale avec graphiques
        self.create_charts_area()
        
        # Zone statistiques
        self.create_stats_area()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.window, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(header, text="📈 TABLEAU DE BORD DÉTAILLÉ", 
                              font=('Arial', 18, 'bold'), bg='#003366', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Bouton fermer
        close_btn = tk.Button(header, text="Fermer", command=self.on_closing,
                              bg='#6c757d', fg='white', font=('Arial', 10),
                              relief=tk.FLAT, cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=20, pady=15)
    
    def create_filters(self):
        """Créer les filtres"""
        filter_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, borderwidth=1)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Période
        period_frame = tk.Frame(filter_frame, bg='white')
        period_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(period_frame, text="Période:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT, padx=(0, 10))
        
        period_combo = ttk.Combobox(period_frame, textvariable=self.selected_period,
                                   values=['Aujourd\'hui', '7jours', '30jours', '3mois'],
                                   state='readonly', width=15)
        period_combo.pack(side=tk.LEFT)
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_data())
        
        # Faculté
        faculty_frame = tk.Frame(filter_frame, bg='white')
        faculty_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(faculty_frame, text="Faculté:", font=('Arial', 11), 
                bg='white').pack(side=tk.LEFT, padx=(0, 10))
        
        # Charger les facultés
        faculties = ['Toutes'] + [f[1] for f in self.database.get_facultes()]
        faculty_combo = ttk.Combobox(faculty_frame, textvariable=self.selected_faculty,
                                    values=faculties, state='readonly', width=20)
        faculty_combo.pack(side=tk.LEFT)
        faculty_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_data())
        
        # Bouton rafraîchir
        refresh_btn = tk.Button(filter_frame, text="🔄 Rafraîchir", 
                               command=self.refresh_data, bg='#007bff', fg='white',
                               font=('Arial', 10), relief=tk.FLAT, cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def create_charts_area(self):
        """Créer la zone des graphiques"""
        charts_frame = tk.Frame(self.window, bg='white')
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuration du grid
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_rowconfigure(1, weight=1)
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        
        # Graphique 1: Évolution des présences
        self.create_attendance_chart(charts_frame, 0, 0)
        
        # Graphique 2: Répartition par faculté
        self.create_faculty_chart(charts_frame, 0, 1)
        
        # Graphique 3: Taux de présence par promotion
        self.create_promotion_chart(charts_frame, 1, 0)
        
        # Graphique 4: Statistiques journalières
        self.create_daily_stats_chart(charts_frame, 1, 1)
    
    def create_attendance_chart(self, parent, row, col):
        """Créer le graphique d'évolution des présences"""
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Titre
        title = tk.Label(frame, text="Évolution des Présences", 
                        font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Créer le graphique
        fig = Figure(figsize=(5, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        # Données simulées
        dates = self.get_date_range()
        presents = np.random.randint(20, 50, len(dates))
        absents = np.random.randint(5, 15, len(dates))
        
        ax.plot(dates, presents, 'g-', label='Présents', linewidth=2)
        ax.plot(dates, absents, 'r-', label='Absents', linewidth=2)
        ax.fill_between(dates, presents, alpha=0.3, color='green')
        ax.fill_between(dates, absents, alpha=0.3, color='red')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Nombre d\'étudiants')
        ax.set_title('Présences vs Absences')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotation des dates
        plt.setp(ax.get_xticklabels(), rotation=45)
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Stocker pour mise à jour
        self.attendance_canvas = canvas
        self.attendance_fig = fig
        self.attendance_ax = ax
    
    def create_faculty_chart(self, parent, row, col):
        """Créer le graphique de répartition par faculté"""
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Titre
        title = tk.Label(frame, text="Répartition par Faculté", 
                        font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Créer le graphique
        fig = Figure(figsize=(5, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        # Données simulées
        faculties = [f[1] for f in self.database.get_facultes()[:5]]  # Limiter à 5 facultés
        students_count = np.random.randint(50, 200, len(faculties))
        colors = plt.cm.Set3(np.linspace(0, 1, len(faculties)))
        
        bars = ax.bar(faculties, students_count, color=colors)
        ax.set_xlabel('Facultés')
        ax.set_ylabel('Nombre d\'étudiants')
        ax.set_title('Étudiants par Faculté')
        
        # Ajouter les valeurs sur les barres
        for bar, count in zip(bars, students_count):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'{count}', ha='center', va='bottom')
        
        # Rotation des labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Stocker pour mise à jour
        self.faculty_canvas = canvas
        self.faculty_fig = fig
        self.faculty_ax = ax
    
    def create_promotion_chart(self, parent, row, col):
        """Créer le graphique de taux de présence par promotion"""
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Titre
        title = tk.Label(frame, text="Taux de Présence par Promotion", 
                        font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Créer le graphique
        fig = Figure(figsize=(5, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        # Données simulées
        promotions = ['L1', 'L2', 'L3', 'M1', 'M2']
        attendance_rates = np.random.uniform(70, 95, len(promotions))
        colors = ['green' if rate > 80 else 'orange' if rate > 70 else 'red' 
                 for rate in attendance_rates]
        
        bars = ax.bar(promotions, attendance_rates, color=colors)
        ax.set_xlabel('Promotions')
        ax.set_ylabel('Taux de présence (%)')
        ax.set_title('Taux de Présence par Promotion')
        ax.set_ylim(0, 100)
        
        # Ajouter les valeurs sur les barres
        for bar, rate in zip(bars, attendance_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{rate:.1f}%', ha='center', va='bottom')
        
        # Ligne de référence à 80%
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Objectif 80%')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Stocker pour mise à jour
        self.promotion_canvas = canvas
        self.promotion_fig = fig
        self.promotion_ax = ax
    
    def create_daily_stats_chart(self, parent, row, col):
        """Créer le graphique des statistiques journalières"""
        frame = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Titre
        title = tk.Label(frame, text="Statistiques Journalières", 
                        font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Créer le graphique
        fig = Figure(figsize=(5, 3), dpi=80)
        ax = fig.add_subplot(111)
        
        # Données simulées
        hours = list(range(8, 18))  # 8h à 17h
        entries = np.random.poisson(10, len(hours))  # Arrivées
        exits = np.random.poisson(8, len(hours))     # Départs
        
        ax.plot(hours, entries, 'b-', label='Entrées', linewidth=2, marker='o')
        ax.plot(hours, exits, 'r-', label='Sorties', linewidth=2, marker='s')
        
        ax.set_xlabel('Heure de la journée')
        ax.set_ylabel('Nombre de pointages')
        ax.set_title('Flux de Pointages Horaire')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xticks(hours[::2])  # Afficher une heure sur deux
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Stocker pour mise à jour
        self.daily_canvas = canvas
        self.daily_fig = fig
        self.daily_ax = ax
    
    def create_stats_area(self):
        """Créer la zone des statistiques"""
        stats_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, borderwidth=1)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Titre
        title = tk.Label(stats_frame, text="STATISTIQUES CLÉS", 
                        font=('Arial', 14, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Grid de statistiques
        stats_container = tk.Frame(stats_frame, bg='white')
        stats_container.pack(fill=tk.X, padx=20, pady=10)
        
        # Variables
        self.total_students_var = tk.StringVar(value="0")
        self.present_today_var = tk.StringVar(value="0")
        self.absent_today_var = tk.StringVar(value="0")
        self.attendance_rate_var = tk.StringVar(value="0%")
        self.late_arrivals_var = tk.StringVar(value="0")
        self.early_departures_var = tk.StringVar(value="0")
        
        # Configuration du grid
        for i in range(3):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Statistiques
        stats_data = [
            ("Total Étudiants", self.total_students_var, "#007bff"),
            ("Présents Aujourd'hui", self.present_today_var, "#28a745"),
            ("Absents Aujourd'hui", self.absent_today_var, "#dc3545"),
            ("Taux Présence", self.attendance_rate_var, "#ffc107"),
            ("Arrivées Tardives", self.late_arrivals_var, "#fd7e14"),
            ("Départs Anticipés", self.early_departures_var, "#6f42c1")
        ]
        
        for i, (label, var, color) in enumerate(stats_data):
            row, col = i // 3, i % 3
            
            stat_card = tk.Frame(stats_container, bg=color, relief=tk.RAISED, borderwidth=2)
            stat_card.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            # Valeur
            value_label = tk.Label(stat_card, textvariable=var, 
                                 font=('Arial', 20, 'bold'), bg=color, fg='white')
            value_label.pack(pady=(10, 5))
            
            # Label
            text_label = tk.Label(stat_card, text=label, 
                                font=('Arial', 10), bg=color, fg='white')
            text_label.pack(pady=(0, 10))
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.window, bg='#f0f0f0', height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Dernière mise à jour
        self.last_update_var = tk.StringVar()
        self.last_update_var.set(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
        
        update_label = tk.Label(footer, textvariable=self.last_update_var, 
                               font=('Arial', 9), bg='#f0f0f0', fg='#666')
        update_label.pack(pady=5)
    
    def get_date_range(self):
        """Générer une plage de dates selon la période sélectionnée"""
        period = self.selected_period.get()
        today = datetime.now().date()
        
        if period == 'Aujourd\'hui':
            dates = [today]
        elif period == '7jours':
            dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        elif period == '30jours':
            dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
        else:  # 3mois
            dates = [today - timedelta(days=i) for i in range(89, -1, -1)]
        
        return dates
    
    def refresh_data(self):
        """Rafraîchir toutes les données"""
        try:
            # Charger les vraies statistiques
            stats = self.database.get_statistics()
            
            # Mettre à jour les variables
            self.total_students_var.set(str(stats.get('total_students', 0)))
            self.present_today_var.set(str(stats.get('present_today', 0)))
            self.absent_today_var.set(str(stats.get('absent_today', 0)))
            self.attendance_rate_var.set(f"{stats.get('attendance_rate', 0):.1f}%")
            self.late_arrivals_var.set(str(stats.get('late_arrivals', 0)))
            self.early_departures_var.set(str(stats.get('early_departures', 0)))
            
            # Mettre à jour l'heure
            self.last_update_var.set(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
            
            # TODO: Mettre à jour les graphiques avec les vraies données
            # Pour l'instant, les graphiques utilisent des données simulées
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du rafraîchissement: {str(e)}")
    
    def on_closing(self):
        """Fermer la fenêtre"""
        self.window.destroy()
