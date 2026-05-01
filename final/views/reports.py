"""
Module Rapports - Système UCC
Génération de rapports et exportations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile

class ReportsScreen:
    def __init__(self, parent, user_data, database):
        self.parent = parent
        self.user_data = user_data
        self.database = database
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Rapports et Exportations")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.report_type = tk.StringVar(value="attendance")
        self.date_from = tk.StringVar()
        self.date_to = tk.StringVar()
        self.selected_faculty = tk.StringVar(value="Toutes")
        self.selected_promotion = tk.StringVar(value="Toutes")
        
        # Initialiser les dates
        self.init_dates()
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les données
        self.load_preview()
        
        # Gérer la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_dates(self):
        """Initialiser les dates par défaut"""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        self.date_from.set(week_ago.strftime("%Y-%m-%d"))
        self.date_to.set(today.strftime("%Y-%m-%d"))
    
    def setup_ui(self):
        """Configurer l'interface"""
        
        # Header
        self.create_header()
        
        # Filtres
        self.create_filters()
        
        # Zone de prévisualisation
        self.create_preview_area()
        
        # Actions
        self.create_actions()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Créer l'en-tête"""
        header = tk.Frame(self.window, bg='#003366', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(header, text="📊 RAPPORTS ET EXPORTATIONS", 
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
        
        # Type de rapport
        type_frame = tk.Frame(filter_frame, bg='white')
        type_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(type_frame, text="Type de rapport:", font=('Arial', 11), 
                bg='white').pack(anchor='w')
        
        report_types = [
            ("Présences", "attendance"),
            ("Étudiants", "students"),
            ("Statistiques", "statistics"),
            ("Absences", "absences")
        ]
        
        for text, value in report_types:
            rb = tk.Radiobutton(type_frame, text=text, variable=self.report_type,
                               value=value, bg='white', font=('Arial', 10))
            rb.pack(anchor='w')
        
        # Filtres de date
        date_frame = tk.Frame(filter_frame, bg='white')
        date_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(date_frame, text="Période:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=(0, 5))
        
        # Date début
        from_frame = tk.Frame(date_frame, bg='white')
        from_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(from_frame, text="Du:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT)
        
        from_entry = ttk.Entry(from_frame, textvariable=self.date_from, width=12)
        from_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Date fin
        to_frame = tk.Frame(date_frame, bg='white')
        to_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(to_frame, text="Au:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT)
        
        to_entry = ttk.Entry(to_frame, textvariable=self.date_to, width=12)
        to_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Filtres faculté/promotion
        filters_frame = tk.Frame(filter_frame, bg='white')
        filters_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(filters_frame, text="Filtres:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=(0, 5))
        
        # Faculté
        faculty_frame = tk.Frame(filters_frame, bg='white')
        faculty_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(faculty_frame, text="Faculté:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT)
        
        faculties = ['Toutes'] + [f[1] for f in self.database.get_facultes()]
        faculty_combo = ttk.Combobox(faculty_frame, textvariable=self.selected_faculty,
                                   values=faculties, state='readonly', width=15)
        faculty_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Promotion
        promotion_frame = tk.Frame(filters_frame, bg='white')
        promotion_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(promotion_frame, text="Promotion:", font=('Arial', 10), 
                bg='white').pack(side=tk.LEFT)
        
        promotions = ['Toutes'] + self.database.get_promotions()
        promotion_combo = ttk.Combobox(promotion_frame, textvariable=self.selected_promotion,
                                      values=promotions, state='readonly', width=15)
        promotion_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bouton appliquer
        apply_btn = tk.Button(filter_frame, text="Appliquer", command=self.load_preview,
                             bg='#007bff', fg='white', font=('Arial', 10, 'bold'),
                             relief=tk.FLAT, cursor='hand2')
        apply_btn.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def create_preview_area(self):
        """Créer la zone de prévisualisation"""
        preview_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, borderwidth=1)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title = tk.Label(preview_frame, text="PRÉVISUALISATION DU RAPPORT", 
                        font=('Arial', 14, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Créer le Treeview pour la prévisualisation
        columns = self.get_report_columns()
        
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, 
                                        show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, 
                                   command=self.preview_tree.yview)
        h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, 
                                   command=self.preview_tree.xview)
        
        self.preview_tree.configure(yscrollcommand=v_scrollbar.set, 
                                  xscrollcommand=h_scrollbar.set)
        
        # Pack
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Statistiques du rapport
        stats_frame = tk.Frame(preview_frame, bg='#f8f9fa')
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.report_stats = tk.StringVar(value="Statistiques: En cours de chargement...")
        stats_label = tk.Label(stats_frame, textvariable=self.report_stats, 
                              font=('Arial', 10), bg='#f8f9fa', fg='#666')
        stats_label.pack(pady=5)
    
    def create_actions(self):
        """Créer les actions d'exportation"""
        actions_frame = tk.Frame(self.window, bg='white', relief=tk.RAISED, borderwidth=1)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Titre
        title = tk.Label(actions_frame, text="ACTIONS D'EXPORTATION", 
                        font=('Arial', 12, 'bold'), bg='white', fg='#003366')
        title.pack(pady=10)
        
        # Boutons d'exportation
        buttons_container = tk.Frame(actions_frame, bg='white')
        buttons_container.pack(pady=10)
        
        # Export Excel
        excel_btn = tk.Button(buttons_container, text="📊 Exporter Excel", 
                            command=self.export_excel, bg='#28a745', fg='white',
                            font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                            cursor='hand2', width=20)
        excel_btn.pack(side=tk.LEFT, padx=10)
        
        # Export PDF
        pdf_btn = tk.Button(buttons_container, text="📄 Exporter PDF", 
                          command=self.export_pdf, bg='#dc3545', fg='white',
                          font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                          cursor='hand2', width=20)
        pdf_btn.pack(side=tk.LEFT, padx=10)
        
        # Imprimer
        print_btn = tk.Button(buttons_container, text="🖨️ Imprimer", 
                            command=self.print_report, bg='#007bff', fg='white',
                            font=('Arial', 11, 'bold'), relief=tk.FLAT, 
                            cursor='hand2', width=20)
        print_btn.pack(side=tk.LEFT, padx=10)
    
    def create_footer(self):
        """Créer le pied de page"""
        footer = tk.Frame(self.window, bg='#f0f0f0', height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_text = tk.Label(footer, text="© 2024 UCC - Module Rapports", 
                               font=('Arial', 9), bg='#f0f0f0', fg='#666')
        footer_text.pack(pady=5)
    
    def get_report_columns(self):
        """Obtenir les colonnes selon le type de rapport"""
        report_type = self.report_type.get()
        
        if report_type == "attendance":
            return ["Date", "Matricule", "Nom", "Faculté", "Promotion", 
                   "Heure Entrée", "Heure Sortie", "Statut"]
        elif report_type == "students":
            return ["Matricule", "Nom", "Postnom", "Prénom", "Email", 
                   "Téléphone", "Faculté", "Promotion", "Statut"]
        elif report_type == "statistics":
            return ["Période", "Total Étudiants", "Présents", "Absents", 
                   "Taux Présence", "Retards", "Départs Anticipés"]
        elif report_type == "absences":
            return ["Date", "Matricule", "Nom", "Faculté", "Promotion", 
                   "Motif", "Justifié"]
        else:
            return ["Colonne 1", "Colonne 2", "Colonne 3"]
    
    def load_preview(self):
        """Charger la prévisualisation du rapport"""
        try:
            # Effacer la prévisualisation actuelle
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Simuler les données selon le type de rapport
            report_type = self.report_type.get()
            
            if report_type == "attendance":
                self.load_attendance_data()
            elif report_type == "students":
                self.load_students_data()
            elif report_type == "statistics":
                self.load_statistics_data()
            elif report_type == "absences":
                self.load_absences_data()
            
            # Mettre à jour les statistiques
            self.update_report_stats()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur chargement prévisualisation: {str(e)}")
    
    def load_attendance_data(self):
        """Charger les données de présence"""
        # Simuler des données de présence
        import random
        from datetime import datetime, timedelta
        
        students = self.database.get_students()
        if not students:
            return
        
        start_date = datetime.strptime(self.date_from.get(), "%Y-%m-%d")
        end_date = datetime.strptime(self.date_to.get(), "%Y-%m-%d")
        
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Jours de semaine
                # Simuler 10-20 pointages par jour
                for _ in range(random.randint(10, 20)):
                    student = random.choice(students)
                    
                    # Accès sécurisé aux données sqlite3.Row
                    try:
                        matricule = student[1] if len(student) > 1 else ''
                        nom = student[2] if len(student) > 2 else ''
                        postnom = student[3] if len(student) > 3 else ''
                        prenom = student[4] if len(student) > 4 else ''
                        faculte = student[11] if len(student) > 11 else ''
                        promotion = student[8] if len(student) > 8 else ''
                    except:
                        continue
                    
                    nom_complet = f"{nom} {postnom or ''} {prenom or ''}".strip()
                    
                    entry_time = f"{random.randint(7, 9):02d}:{random.randint(0, 59):02d}"
                    exit_time = f"{random.randint(16, 18):02d}:{random.randint(0, 59):02d}"
                    
                    status = "Présent" if int(entry_time.split(':')[0]) <= 8 else "Retard"
                    
                    self.preview_tree.insert('', 'end', values=(
                        current_date.strftime("%Y-%m-%d"),
                        matricule,
                        nom_complet,
                        faculte,
                        promotion,
                        entry_time,
                        exit_time,
                        status
                    ))
            
            current_date += timedelta(days=1)
    
    def load_students_data(self):
        """Charger les données des étudiants"""
        students = self.database.get_students()
        
        for student in students:
            try:
                matricule = student[1] if len(student) > 1 else ''
                nom = student[2] if len(student) > 2 else ''
                postnom = student[3] if len(student) > 3 else ''
                prenom = student[4] if len(student) > 4 else ''
                email = student[5] if len(student) > 5 else ''
                telephone = student[6] if len(student) > 6 else ''
                faculte = student[11] if len(student) > 11 else ''
                promotion = student[8] if len(student) > 8 else ''
                statut = student[9] if len(student) > 9 else ''
            except:
                continue
            
            self.preview_tree.insert('', 'end', values=(
                matricule,
                nom,
                postnom,
                prenom,
                email,
                telephone,
                faculte,
                promotion,
                statut
            ))
    
    def load_statistics_data(self):
        """Charger les données statistiques"""
        # Simuler des données statistiques
        import random
        
        periods = ["Semaine 1", "Semaine 2", "Semaine 3", "Semaine 4"]
        
        for period in periods:
            total = random.randint(150, 200)
            present = random.randint(120, total)
            absent = total - present
            rate = (present / total) * 100
            late = random.randint(5, 20)
            early = random.randint(3, 15)
            
            self.preview_tree.insert('', 'end', values=(
                period,
                total,
                present,
                absent,
                f"{rate:.1f}%",
                late,
                early
            ))
    
    def load_absences_data(self):
        """Charger les données d'absences"""
        import random
        from datetime import datetime, timedelta
        
        students = self.database.get_students()
        if not students:
            return
        
        start_date = datetime.strptime(self.date_from.get(), "%Y-%m-%d")
        end_date = datetime.strptime(self.date_to.get(), "%Y-%m-%d")
        
        # Simuler 5-15 absences sur la période
        for _ in range(random.randint(5, 15)):
            student = random.choice(students)
            absence_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            
            try:
                matricule = student[1] if len(student) > 1 else ''
                nom = student[2] if len(student) > 2 else ''
                postnom = student[3] if len(student) > 3 else ''
                prenom = student[4] if len(student) > 4 else ''
                faculte = student[11] if len(student) > 11 else ''
                promotion = student[8] if len(student) > 8 else ''
            except:
                continue
            
            nom_complet = f"{nom} {postnom or ''} {prenom or ''}".strip()
            
            motifs = ["Maladie", "Famille", "Transport", "Autre"]
            motif = random.choice(motifs)
            justifie = "Oui" if random.random() > 0.3 else "Non"
            
            self.preview_tree.insert('', 'end', values=(
                absence_date.strftime("%Y-%m-%d"),
                matricule,
                nom_complet,
                faculte,
                promotion,
                motif,
                justifie
            ))
    
    def update_report_stats(self):
        """Mettre à jour les statistiques du rapport"""
        total_items = len(self.preview_tree.get_children())
        
        if total_items == 0:
            self.report_stats.set("Aucune donnée trouvée pour les critères sélectionnés")
            return
        
        report_type = self.report_type.get()
        
        if report_type == "attendance":
            presents = len([item for item in self.preview_tree.get_children() 
                           if self.preview_tree.item(item)['values'][7] in ["Présent", "Retard"]])
            rate = (presents / total_items) * 100
            self.report_stats.set(f"Total: {total_items} | Présents: {presents} | Taux: {rate:.1f}%")
        
        elif report_type == "students":
            actifs = len([item for item in self.preview_tree.get_children() 
                         if len(self.preview_tree.item(item)['values']) > 8 and 
                         self.preview_tree.item(item)['values'][8] == 'actif'])
            self.report_stats.set(f"Total: {total_items} | Actifs: {actifs} | Inactifs: {total_items - actifs}")
        
        else:
            self.report_stats.set(f"Total: {total_items} enregistrements")
    
    def export_excel(self):
        """Exporter en Excel"""
        try:
            # Obtenir les données
            data = []
            columns = self.get_report_columns()
            
            for item in self.preview_tree.get_children():
                data.append(self.preview_tree.item(item)['values'])
            
            if not data:
                messagebox.showwarning("Avertissement", "Aucune donnée à exporter")
                return
            
            # Créer le DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Demander le fichier de destination
            file_path = filedialog.asksaveasfilename(
                title="Sauvegarder le rapport Excel",
                defaultextension=".xlsx",
                filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")]
            )
            
            if not file_path:
                return
            
            # Exporter
            df.to_excel(file_path, index=False)
            
            messagebox.showinfo("Succès", f"Rapport exporté avec succès:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur exportation Excel: {str(e)}")
    
    def export_pdf(self):
        """Exporter en PDF"""
        try:
            # Obtenir les données
            data = []
            columns = self.get_report_columns()
            
            for item in self.preview_tree.get_children():
                data.append(self.preview_tree.item(item)['values'])
            
            if not data:
                messagebox.showwarning("Avertissement", "Aucune donnée à exporter")
                return
            
            # Demander le fichier de destination
            file_path = filedialog.asksaveasfilename(
                title="Sauvegarder le rapport PDF",
                defaultextension=".pdf",
                filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
            )
            
            if not file_path:
                return
            
            # Créer une image simple pour le rapport
            self.create_pdf_report(file_path, data, columns)
            
            messagebox.showinfo("Succès", f"Rapport exporté avec succès:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur exportation PDF: {str(e)}")
    
    def create_pdf_report(self, file_path, data, columns):
        """Créer un rapport PDF simple"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            # Créer le document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title = Paragraph(f"Rapport {self.report_type.get().title()}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Période
            period = Paragraph(f"Période: {self.date_from.get()} au {self.date_to.get()}", styles['Normal'])
            story.append(period)
            story.append(Spacer(1, 12))
            
            # Tableau de données
            table_data = [columns] + data
            table = Table(table_data)
            
            # Style du tableau
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            
            # Générer le PDF
            doc.build(story)
            
        except ImportError:
            # Si reportlab n'est pas installé, créer une version texte simple
            self.create_simple_text_report(file_path, data, columns)
    
    def create_simple_text_report(self, file_path, data, columns):
        """Créer un rapport texte simple si reportlab n'est pas disponible"""
        with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(f"RAPPORT {self.report_type.get().upper()}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Période: {self.date_from.get()} au {self.date_to.get()}\n")
            f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # En-têtes
            f.write("\t".join(columns) + "\n")
            f.write("-" * (len(columns) * 15) + "\n")
            
            # Données
            for row in data:
                f.write("\t".join(str(item) for item in row) + "\n")
            
            f.write(f"\nTotal: {len(data)} enregistrements\n")
    
    def print_report(self):
        """Imprimer le rapport"""
        try:
            # Pour l'instant, exporter vers un fichier temporaire et suggérer l'impression
            messagebox.showinfo("Impression", "Fonction d'impression en développement.\nVous pouvez exporter en PDF ou Excel puis imprimer.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur impression: {str(e)}")
    
    def on_closing(self):
        """Fermer la fenêtre"""
        self.window.destroy()
