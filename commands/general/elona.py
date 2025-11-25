# commands/general/elona.py

import discord
from discord import app_commands
from datetime import timedelta

from core.history import init_history, add_to_history, historiques_salons
from core.ai import generate_reply
# from data.data import * <- Cet import n'est pas utilisé, on l'enlève
from config.settings import PROMPT_ELONA

# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="elona",
        description="Analyse la discussion du salon avec la personnalité Elona."
    )
    async def elona_cmd(interaction: discord.Interaction):
        channel = interaction.channel
        channel_id = channel.id

        # --- 1) Récupération des messages récents du salon ---
        now = discord.utils.utcnow()
        cutoff = now - timedelta(hours=24)

        messages = []
        async for msg in channel.history(limit=200):
            if msg.created_at < cutoff:
                break
            if msg.author.id == bot.user.id:
                continue
            if msg.content:
                messages.append(msg)

        # --- 2) Reset l’historique du salon avec la personnalité Elona ---
        # On suppose que init_history est valide (on le corrigera après)
        historiques_salons[channel_id] = init_history(PROMPT_ELONA)

        # ajoute les 30 derniers messages uniquement
        for m in reversed(messages[-30:]):
            # On récupère le nom de l'auteur pour préfixer le message
            author_name = m.author.display_name if m.guild else m.author.name
            
            # On suppose que add_to_history est valide
            # On envoie le message préfixé : "NomUtilisateur: Texte du message"
            add_to_history(channel_id, "user", f"{author_name}: {m.content}")

        # --- 3) Interaction Discord ---
        # "Thinking... (public)" -> C'est correct
        await interaction.response.defer(thinking=True)

        # Génération IA (maintenant asynchrone)
        rep = await generate_reply(channel_id)

        # --- 4) Envoi final ---
        # On modifie le message "Thinking..."
        await interaction.edit_original_response(content=rep)