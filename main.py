"""
main.py — Point d'entrée du projet
---------------------------------
But: fichier minimal/placeholder actuellement contenant uniquement l'identifiant `bot`.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import confidentiel
from core.bot import ElonaBot

bot = ElonaBot(prefix="/")

bot.run(confidentiel.TOKENELONA)
