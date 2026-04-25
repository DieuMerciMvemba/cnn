# UTILITAIRE CSV POUR POINTAGE UCC
# Outils pour gérer les fichiers CSV

import csv
import os
from datetime import datetime

class CSVManager:
    def __init__(self):
        self.students_file = "students.csv"
        self.attendance_file = "attendance.csv"
    
    def show_all_students(self):
        """Afficher tous les étudiants"""
        print("\n" + "="*50)
        print("LISTE DES ÉTUDIANTS")
        print("="*50)
        
        if not os.path.exists(self.students_file):
            print("Aucun fichier étudiants trouvé")
            return
        
        with open(self.students_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:  # En-tête
                    print(f"{'ID':<15} {'Nom':<20} {'Image':<25}")
                    print("-" * 60)
                else:
                    print(f"{row[0]:<15} {row[1]:<20} {row[2]:<25}")
        
        print("="*50)
    
    def show_attendance_today(self):
        """Afficher les présences du jour"""
        print("\n" + "="*50)
        print("PRÉSENCES DU JOUR")
        print("="*50)
        
        if not os.path.exists(self.attendance_file):
            print("Aucun fichier présence trouvé")
            return
        
        today = datetime.now().strftime('%Y-%m-%d')
        count = 0
        
        with open(self.attendance_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:  # En-tête
                    print(f"{'ID':<15} {'Nom':<20} {'Heure':<10}")
                    print("-" * 45)
                elif len(row) > 0 and row[2].startswith(today):
                    time = row[2].split(' ')[1]
                    print(f"{row[0]:<15} {row[1]:<20} {time:<10}")
                    count += 1
        
        print(f"\nTotal: {count} présences")
        print("="*50)
    
    def show_attendance_all(self):
        """Afficher toutes les présences"""
        print("\n" + "="*50)
        print("HISTORIQUE DES PRÉSENCES")
        print("="*50)
        
        if not os.path.exists(self.attendance_file):
            print("Aucun fichier présence trouvé")
            return
        
        with open(self.attendance_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i == 0:  # En-tête
                    print(f"{'ID':<15} {'Nom':<20} {'Date':<12} {'Heure':<8}")
                    print("-" * 55)
                else:
                    date_time = row[2].split(' ')
                    print(f"{row[0]:<15} {row[1]:<20} {date_time[0]:<12} {date_time[1]:<8}")
        
        print("="*50)
    
    def export_attendance_report(self, date=None):
        """Exporter un rapport de présence"""
        filename = f"rapport_presence_{date or datetime.now().strftime('%Y-%m-%d')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("RAPPORT DE PRÉSENCE UCC\n")
            file.write("="*50 + "\n")
            file.write(f"Date: {date or datetime.now().strftime('%Y-%m-%d')}\n\n")
            
            if os.path.exists(self.attendance_file):
                with open(self.attendance_file, 'r', encoding='utf-8') as csv_file:
                    reader = csv.reader(csv_file)
                    count = 0
                    
                    for row in reader:
                        if len(row) > 0 and (date is None or row[2].startswith(date)):
                            file.write(f"✅ {row[1]} - {row[2]}\n")
                            count += 1
                    
                    file.write(f"\nTotal: {count} présences\n")
        
        print(f"Rapport exporté: {filename}")

def main():
    """Menu principal"""
    manager = CSVManager()
    
    while True:
        print("\n" + "="*40)
        print("GESTION CSV - POINTAGE UCC")
        print("="*40)
        print("1. Voir tous les étudiants")
        print("2. Voir présences du jour")
        print("3. Voir historique complet")
        print("4. Exporter rapport du jour")
        print("5. Exporter rapport (date)")
        print("6. Quitter")
        
        choice = input("Choix: ")
        
        if choice == "1":
            manager.show_all_students()
        elif choice == "2":
            manager.show_attendance_today()
        elif choice == "3":
            manager.show_attendance_all()
        elif choice == "4":
            manager.export_attendance_report()
        elif choice == "5":
            date = input("Date (AAAA-MM-JJ): ")
            manager.export_attendance_report(date)
        elif choice == "6":
            break
        else:
            print("Choix invalide")

if __name__ == "__main__":
    main()
