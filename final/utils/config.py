"""
Configuration du système UCC
Paramètres et constantes
"""

import os

# Chemins de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
STUDENT_PHOTOS_DIR = os.path.join(BASE_DIR, "student_photos")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Créer les répertoires nécessaires
for directory in [DATABASE_DIR, CAPTURES_DIR, STUDENT_PHOTOS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuration base de données
DATABASE_PATH = os.path.join(DATABASE_DIR, "ucc_system.db")

# Configuration caméra
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Configuration reconnaissance faciale
FACE_RECOGNITION_MODEL = "VGG-Face"
FACE_CONFIDENCE_THRESHOLD = 0.6
FACE_CACHE_TIMEOUT = 5  # secondes
MIN_FACE_SIZE = (64, 64)

# Configuration pointage
ATTENDANCE_TIMEOUT = 300  # 5 minutes entre pointages
LATE_HOUR = 8  # Heure de retard
LATE_MINUTE = 0

# Configuration interface
WINDOW_TITLE = "Système de Pointage UCC - Reconnaissance Faciale"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
UPDATE_INTERVAL = 30  # millisecondes

# Couleurs UCC
UCC_BLUE = "#003366"
UCC_LIGHT_BLUE = "#E6F2FF"
UCC_WHITE = "#FFFFFF"
UCC_GRAY = "#F0F0F0"

# Facultés UCC
UCC_FACULTIES = [
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

# Promotions
UCC_PROMOTIONS = [
    "LICENCE 1",
    "LICENCE 2", 
    "LICENCE 3",
    "MASTER 1",
    "MASTER 2"
]

# Configuration exports
EXCEL_TEMPLATE_PATH = os.path.join(REPORTS_DIR, "templates")
PDF_TEMPLATE_PATH = os.path.join(REPORTS_DIR, "templates")

# Configuration logs
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(BASE_DIR, "logs", "ucc_system.log")

# Sécurité
SESSION_TIMEOUT = 1800  # 30 minutes
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 8

# Performance
MAX_COMPARISONS_PER_FRAME = 10
THREAD_POOL_SIZE = 4
CACHE_SIZE_LIMIT = 100

# Messages système
MESSAGES = {
    'camera_ready': "Caméra prête",
    'camera_error': "Erreur de caméra",
    'recognition_ready': "Reconnaissance prête",
    'attendance_marked': "Présence marquée avec succès",
    'already_marked': "Déjà pointé aujourd'hui",
    'face_not_recognized': "Visage non reconnu",
    'system_ready': "Système prêt",
    'system_error': "Erreur système"
}

# Formats de date/heure
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

# Extensions de fichiers
SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']
SUPPORTED_EXPORT_FORMATS = ['.xlsx', '.pdf', '.csv']
