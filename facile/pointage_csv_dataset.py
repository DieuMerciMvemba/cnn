# SYSTÈME DE POINTAGE UCC AVEC CSV ET DATASET
# Stockage CSV + Images de référence dans Dataset/

import cv2
import csv
import os
import datetime
from deepface import DeepFace

class AttendanceSystemCSV:
    def __init__(self):
        # Initialiser la webcam
        self.cap = cv2.VideoCapture(0)
        
        # Dossiers et fichiers
        self.dataset_folder = "Dataset"
        self.students_file = "students.csv"
        self.attendance_file = "attendance.csv"
        
        # Créer les fichiers CSV
        self.create_csv_files()
        
        # Charger les étudiants depuis le Dataset
        self.load_students_from_dataset()
        
        print("Système de pointage UCC CSV prêt")
    
    def create_csv_files(self):
        """Créer les fichiers CSV s'ils n'existent pas"""
        
        # Fichier étudiants
        if not os.path.exists(self.students_file):
            with open(self.students_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['student_id', 'name', 'image_file'])
        
        # Fichier présence
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['student_id', 'name', 'timestamp', 'status'])
        
        print("Fichiers CSV créés/vérifiés")
    
    def load_students_from_dataset(self):
        """Charger les étudiants depuis les images du Dataset"""
        self.students = {}
        
        if not os.path.exists(self.dataset_folder):
            print(f"Dossier {self.dataset_folder} non trouvé")
            return
        
        # Parcourir les images du Dataset
        for filename in os.listdir(self.dataset_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Extraire le nom de l'étudiant du nom de fichier
                name = os.path.splitext(filename)[0]
                student_id = name.replace(' ', '_').lower()
                
                # Ajouter à la base
                self.students[student_id] = {
                    'name': name,
                    'image_file': filename,
                    'path': os.path.join(self.dataset_folder, filename)
                }
                
                # Ajouter au CSV si pas encore présent
                self.add_student_to_csv(student_id, name, filename)
        
        print(f"Étudiants chargés: {len(self.students)}")
        for student_id, info in self.students.items():
            print(f"  - {info['name']} ({student_id})")
    
    def add_student_to_csv(self, student_id, name, image_file):
        """Ajouter un étudiant au fichier CSV"""
        # Vérifier si déjà présent
        if os.path.exists(self.students_file):
            with open(self.students_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) > 0 and row[0] == student_id:
                        return  # Déjà présent
        
        # Ajouter
        with open(self.students_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([student_id, name, image_file])
    
    def recognize_face(self, face_image):
        """Reconnaître un visage avec DeepFace"""
        try:
            # Comparer avec chaque étudiant du Dataset
            for student_id, student_info in self.students.items():
                reference_path = student_info['path']
                
                # Vérifier si l'image de référence existe
                if not os.path.exists(reference_path):
                    continue
                
                # Comparer avec DeepFace
                result = DeepFace.verify(
                    face_image,
                    reference_path,
                    model_name='VGG-Face',
                    enforce_detection=False
                )
                
                if result['verified']:
                    return student_id, student_info['name']
        
        except Exception as e:
            print(f"Erreur reconnaissance: {e}")
        
        return None, None
    
    def mark_attendance_csv(self, student_id, name):
        """Marquer la présence dans le fichier CSV"""
        # Vérifier si déjà marqué aujourd'hui
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        if os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if (len(row) > 0 and 
                        row[0] == student_id and 
                        row[2].startswith(today)):
                        print(f"Présence déjà marquée pour {name}")
                        return False
        
        # Marquer la présence
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.attendance_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([student_id, name, timestamp, "Présent"])
        
        print(f"Présence marquée: {name} à {timestamp}")
        return True
    
    def run(self):
        """Démarrer le système de pointage"""
        print("\nDémarrage du système de pointage UCC CSV...")
        print("Instructions:")
        print("- Placez votre visage devant la caméra")
        print("- Appuyez sur 'q' pour quitter")
        print("- Appuyez sur 's' pour voir les statistiques")
        
        # Charger le détecteur de visage
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            # Détecter les visages
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            
            # Traiter chaque visage
            for (x, y, w, h) in faces:
                # Extraire le visage
                face_roi = frame[y:y+h, x:x+w]
                
                # Reconnaître le visage
                student_id, name = self.recognize_face(face_roi)
                
                if student_id:
                    # Visage reconnu
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # Marquer automatiquement la présence
                    self.mark_attendance_csv(student_id, name)
                else:
                    # Visage non reconnu
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, 'Inconnu', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            # Informations
            cv2.putText(frame, f'Visages: {len(faces)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Étudiants: {len(self.students)}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, 'q=quitter s=stats', (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Pointage UCC - CSV + Dataset', frame)
            
            # Contrôles
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.show_statistics()
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("Système arrêté")
    
    def show_statistics(self):
        """Afficher les statistiques"""
        print("\n" + "="*50)
        print("STATISTIQUES DU JOUR")
        print("="*50)
        
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        today_attendance = 0
        
        if os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) > 0 and row[2].startswith(today):
                        today_attendance += 1
                        print(f"✅ {row[1]} - {row[2]}")
        
        print(f"\nTotal présences aujourd'hui: {today_attendance}")
        print(f"Total étudiants: {len(self.students)}")
        print(f"Taux de présence: {today_attendance}/{len(self.students)}")
        print("="*50)

if __name__ == "__main__":
    system = AttendanceSystemCSV()
    system.run()
