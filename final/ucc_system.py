"""
Application Principale - Système UCC
Point d'entrée avec écran de connexion
"""

import tkinter as tk
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.login import LoginScreen

def main():
    """Fonction principale"""
    # Créer la fenêtre principale
    root = tk.Tk()
    
    # Configuration de la fenêtre
    root.withdraw()  # Cacher temporairement
    
    # Lancer l'écran de connexion
    app = LoginScreen(root)
    
    # Afficher la fenêtre
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()
