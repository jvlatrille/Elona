# events/on_message.py

import discord
from core.ai import generate_reply
from core.history import add_to_history
import confidentiel

# La fonction setup DOIT être asynchrone
async def setup(bot):
    
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        # --- Traitement du message ---
        content = message.content
        if message.attachments:
            content += " (note : pièce jointe non lisible)"

        # Variable pour l'ID du salon (ou de l'auteur en DM)
        cid = None

        # Cas 1 : DM
        if isinstance(message.channel, discord.DMChannel):
            cid = message.author.id
        
        # Cas 2 : Serveur autorisé
        elif message.guild and message.guild.id == confidentiel.SERVEUR_CIBLE:
            if not confidentiel.SALONS_AUTORISES or message.channel.id in confidentiel.SALONS_AUTORISES:
                cid = message.channel.id
        
        # --- Si le message est dans un contexte valide (DM ou salon autorisé) ---
        if cid:
            try:
                # On ajoute à l'historique
                add_to_history(cid, "user", content)
                
                # On génère la réponse (asynchrone)
                rep = await generate_reply(cid)
                
                # On envoie la réponse
                await message.channel.send(rep)
                
                # On arrête le traitement pour ne pas exécuter bot.process_commands
                return 
            except Exception as e:
                print(f"Erreur lors du traitement on_message pour {cid}: {e}")
                # On évite de planter si l'IA ou l'historique échoue
                return

        # --- Si le message n'était NI en DM, NI dans un salon autorisé ---
        # On traite les commandes normales (ex: /anime)
        await bot.process_commands(message)