# core/bot.py
import os
import importlib  # On peut même le supprimer si tu veux
import discord
from discord.ext import commands

class ElonaBot(commands.Bot):
    def __init__(self, prefix: str):
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=prefix,
            intents=intents,
            description="Bot Discord — Elona"
        )

    async def setup_hook(self):
        """
        Chargé automatiquement au démarrage du bot.
        On y charge :
        - les events/
        - les commands/
        """

        # === Events ===
        events_path = os.path.join(os.path.dirname(__file__), "..", "events")
        # On AWAIT la fonction maintenant
        await self.load_modules_from_path(events_path, "events")

        # === Commands ===
        commands_path = os.path.join(os.path.dirname(__file__), "..", "commands")
        # On AWAIT la fonction maintenant
        await self.load_commands_from_path(commands_path, "commands")

        print("Toutes les extensions ont été chargées.")
        
        # === Synchronisation ===
        # Il est PRÉFÉRABLE de synchroniser les commandes APRÈS les avoir toutes chargées.
        # Déplaçons la logique de on_ready.py ici.
        try:
            await self.tree.sync()
            print("Commandes synchronisées avec Discord.")
        except Exception as e:
            print(f"Erreur lors de la synchronisation : {e}")


    async def load_modules_from_path(self, path, package): # <-- Rendre ASYNC
        """
        Charge tous les fichiers .py du dossier events/
        """
        for file in os.listdir(path):
            if file.endswith(".py"):
                mod_name = file[:-3]
                if mod_name == "__init__":
                    continue

                full_name = f"{package}.{mod_name}" # ex: "events.on_ready"
                try:
                    # C'est LA modification principale :
                    await self.load_extension(full_name) 
                    print(f"[event] chargé : {full_name}")
                except Exception as e:
                    print(f"Erreur chargement event {full_name} : {e}")

    async def load_commands_from_path(self, root, package): # <-- Rendre ASYNC
        """
        Charge les commandes dans commands/
        et dans les sous-dossiers admin/, fun/, general/
        """
        for dirpath, _, files in os.walk(root, topdown=True):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    rel_path = os.path.relpath(dirpath, root)
                    
                    # Correction du bug pour les fichiers à la racine (si rel_path est '.')
                    if rel_path == ".":
                        mod_parts = [file[:-3]]
                    else:
                        mod_parts = rel_path.split(os.sep)
                        mod_parts.append(file[:-3])
                    
                    # ex: "commands.general.ping"
                    mod_name = package + "." + ".".join(mod_parts) 

                    try:
                        # C'est LA modification principale :
                        await self.load_extension(mod_name)
                        print(f"[cmd] chargée : {mod_name}")
                    except Exception as e:
                        print(f"Erreur chargement commande {mod_name} : {e}")