"""
Base de données SQLite pour le système UCC
Structure complète avec étudiants, facultés, promotions
"""

import sqlite3
import os
from datetime import datetime
import hashlib

class DatabaseUCC:
    def __init__(self, db_path="database/ucc_system.db"):
        self.db_path = db_path
        self.ensure_database_directory()
        self.init_database()
    
    def ensure_database_directory(self):
        """Créer le dossier database s'il n'existe pas"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Obtenir une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        return conn
    
    def init_database(self):
        """Initialiser toutes les tables de la base de données"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des facultés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facultes (
                    id INTEGER PRIMARY KEY,
                    nom TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des étudiants UCC
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matricule TEXT UNIQUE NOT NULL,
                    nom TEXT NOT NULL,
                    postnom TEXT,
                    prenom TEXT,
                    faculte_id INTEGER,
                    promotion TEXT NOT NULL,
                    email TEXT,
                    telephone TEXT,
                    photo_path TEXT,
                    statut TEXT DEFAULT 'actif',
                    date_inscription DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (faculte_id) REFERENCES facultes(id)
                )
            ''')
            
            # Table des pointages (attendance)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    type_pointage TEXT DEFAULT 'entree',
                    statut TEXT DEFAULT 'present',
                    confidence_score REAL,
                    photo_capture_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            ''')
            
            # Table des utilisateurs (admin/surveillants)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'surveillant',
                    faculte_access TEXT, -- JSON list des facultés accessibles
                    nom_complet TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des logs d'actions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Table des photos étudiantes (pour DeepFace)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    photo_path TEXT NOT NULL,
                    photo_type TEXT DEFAULT 'reference', -- reference, capture
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            ''')
            
            conn.commit()
    
    def init_facultes(self):
        """Initialiser les facultés de l'UCC"""
        facultes_ucc = [
            "Faculté d'Économie et Développement",
            "Faculté de Sciences Informatiques",
            "Faculté de Sciences Politique",
            "Faculté de Théologie",
            "Faculté de Philosophie",
            "Faculté de Droit Canonique",
            "Faculté de Communication Sociale",
            "Faculté de Médecine",
            "Faculté de Droit"
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for faculte in facultes_ucc:
                cursor.execute('''
                    INSERT OR IGNORE INTO facultes (nom) VALUES (?)
                ''', (faculte,))
            conn.commit()
    
    def create_admin_user(self):
        """Créer l'utilisateur administrateur par défaut"""
        password_hash = self.hash_password("admin123")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (username, password_hash, role, nom_complet) 
                VALUES (?, ?, ?, ?)
            ''', ("admin", password_hash, "admin", "Administrateur UCC"))
            conn.commit()
    
    def hash_password(self, password):
        """Hasher un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hash_password):
        """Vérifier un mot de passe"""
        return self.hash_password(password) == hash_password
    
    def generate_matricule(self, faculte_id, student_id):
        """Générer un matricule automatique UCC-ANNEE-FACULTE-ID"""
        year = datetime.now().year
        return f"UCC-{year}-{faculte_id}-{student_id:04d}"
    
    def get_facultes(self):
        """Obtenir la liste des facultés"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM facultes ORDER BY nom")
            return cursor.fetchall()
    
    def get_promotions(self):
        """Obtenir la liste des promotions"""
        return ["LICENCE 1", "LICENCE 2", "LICENCE 3", "MASTER 1", "MASTER 2"]
    
    def add_student(self, nom, postnom, prenom, faculte_id, promotion, email="", telephone=""):
        """Ajouter un nouvel étudiant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Générer matricule
            cursor.execute("SELECT MAX(id) FROM students")
            max_id = cursor.fetchone()[0] or 0
            matricule = self.generate_matricule(faculte_id, max_id + 1)
            
            # Insérer l'étudiant
            cursor.execute('''
                INSERT INTO students 
                (matricule, nom, postnom, prenom, faculte_id, promotion, email, telephone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (matricule, nom, postnom, prenom, faculte_id, promotion, email, telephone))
            
            student_id = cursor.lastrowid
            conn.commit()
            
            return student_id, matricule
    
    def get_students(self, faculte_id=None, promotion=None, search=""):
        """Obtenir la liste des étudiants avec filtres"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT s.*, f.nom as faculte_nom 
                FROM students s 
                LEFT JOIN facultes f ON s.faculte_id = f.id 
                WHERE s.statut = 'actif'
            '''
            params = []
            
            if faculte_id:
                query += " AND s.faculte_id = ?"
                params.append(faculte_id)
            
            if promotion:
                query += " AND s.promotion = ?"
                params.append(promotion)
            
            if search:
                query += " AND (s.nom LIKE ? OR s.postnom LIKE ? OR s.prenom LIKE ? OR s.matricule LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term, search_term])
            
            query += " ORDER BY s.nom, s.prenom"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def mark_attendance(self, student_id, type_pointage='entree', confidence_score=None, photo_path=None):
        """Marquer la présence d'un étudiant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si déjà pointé aujourd'hui (même type)
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT id FROM attendance 
                WHERE student_id = ? AND DATE(timestamp) = ? AND type_pointage = ?
            ''', (student_id, today, type_pointage))
            
            if cursor.fetchone():
                return False  # Déjà pointé
            
            # Déterminer le statut
            current_time = datetime.now().time()
            statut = 'present'
            if current_time.hour > 8:  # Après 8h = retard
                statut = 'retard'
            
            # Marquer la présence
            cursor.execute('''
                INSERT INTO attendance 
                (student_id, type_pointage, statut, confidence_score, photo_capture_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, type_pointage, statut, confidence_score, photo_path))
            
            conn.commit()
            return True
    
    def get_attendance_today(self, faculte_id=None):
        """Obtenir les présences du jour"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT a.*, s.nom, s.postnom, s.prenom, s.matricule, 
                       f.nom as faculte_nom, s.promotion
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                LEFT JOIN facultes f ON s.faculte_id = f.id
                WHERE DATE(a.timestamp) = DATE('now')
            '''
            params = []
            
            if faculte_id:
                query += " AND s.faculte_id = ?"
                params.append(faculte_id)
            
            query += " ORDER BY a.timestamp DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_statistics(self, faculte_id=None):
        """Obtenir les statistiques de présence"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total étudiants
            query_students = "SELECT COUNT(*) FROM students WHERE statut = 'actif'"
            params_students = []
            if faculte_id:
                query_students += " AND faculte_id = ?"
                params_students.append(faculte_id)
            
            cursor.execute(query_students, params_students)
            total_students = cursor.fetchone()[0]
            
            # Présents aujourd'hui
            query_present = '''
                SELECT COUNT(DISTINCT student_id) 
                FROM attendance 
                WHERE DATE(timestamp) = DATE('now')
            '''
            params_present = []
            if faculte_id:
                query_present += '''
                    AND student_id IN (
                        SELECT id FROM students WHERE faculte_id = ?
                    )
                '''
                params_present.append(faculte_id)
            
            cursor.execute(query_present, params_present)
            present_today = cursor.fetchone()[0]
            
            return {
                'total_students': total_students,
                'present_today': present_today,
                'absent_today': total_students - present_today,
                'attendance_rate': (present_today / total_students * 100) if total_students > 0 else 0
            }
    
    def log_action(self, user_id, action, details=""):
        """Enregistrer une action dans les logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO action_logs (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            conn.commit()

# Test de la base de données
if __name__ == "__main__":
    db = DatabaseUCC()
    db.init_facultes()
    db.create_admin_user()
    
    print("Base de données UCC initialisée avec succès!")
    print("Facultés:", len(db.get_facultes()))
    print("Promotions:", db.get_promotions())
