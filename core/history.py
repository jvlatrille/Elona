# core/history.py

from config.settings import PROMPT_GENERAL

historiques_salons = {}

def init_history(prompt=PROMPT_GENERAL):
    return [{"role": "system", "content": prompt}]

def add_to_history(channel_id, role, content):
    if channel_id not in historiques_salons:
        historiques_salons[channel_id] = init_history()
    historiques_salons[channel_id].append({"role": role, "content": content})

def get_history(channel_id):
    """
    Récupère l'historique d'un salon, ou en crée un vide s'il n'existe pas.
    """
    if channel_id not in historiques_salons:
        historiques_salons[channel_id] = init_history()
    
    return historiques_salons[channel_id]