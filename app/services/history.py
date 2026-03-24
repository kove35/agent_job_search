# app/services/history.py
import os
import json
from typing import List, Dict, Any
from pathlib import Path

# =========================================================
# 📂 HISTORIQUE DES CANDIDATURES
# =========================================================
HISTORY_FOLDER = "storage/history"
APPLICATIONS_FILE = os.path.join(HISTORY_FOLDER, "applications.json")

# Créer le dossier s'il n'existe pas
os.makedirs(HISTORY_FOLDER, exist_ok=True)


def get_applications_history() -> List[Dict[str, Any]]:
    """
    🎯 Récupère l'historique des candidatures
    
    Returns:
        Liste des candidatures sauvegardées
    """
    try:
        if os.path.exists(APPLICATIONS_FILE):
            with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception:
        return []


def save_application(application: Dict[str, Any]) -> bool:
    """
    💾 Sauvegarde une candidature dans l'historique
    """
    try:
        history = get_applications_history()
        history.append(application)
        
        with open(APPLICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception:
        return False