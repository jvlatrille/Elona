# events/on_message.py (Correction de la logique de ciblage)

import discord
from core.ai import generate_reply
from core.history import add_to_history
import confidentiel
from utils.typing_helper import send_with_typing

async def setup(bot):

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        # --- Détermination du contexte et de la réaction ---
        channel_id = message.channel.id
        guild_id = message.guild.id if message.guild else None

        # 1. Vérifie si c'est un message privé (DM)
        if isinstance(message.channel, discord.DMChannel):
            cid = message.author.id
            do_react = True

        # 2. Vérifie si c'est un salon ciblé (addition)
        elif channel_id in confidentiel.SALONS_AUTORISES:
            cid = channel_id
            do_react = True

        # 3. Vérifie si c'est le serveur cible (répond à tout)
        elif guild_id == confidentiel.SERVEUR_CIBLE:
            cid = channel_id
            do_react = True

        # 4. Par défaut, on ne réagit pas
        else:
            do_react = False
            cid = None

        # --- Exécution de la réaction IA si do_react est True ---
        if do_react and cid:
            content = message.content
            if message.attachments:
                content += " (note : pièce jointe non lisible)"

            try:
                add_to_history(cid, "user", content)
                rep = await generate_reply(cid)
                await send_with_typing(message.channel, lambda: message.channel.send(rep))
                return

            except Exception as e:
                print(f"Erreur lors du traitement on_message pour {cid}: {e}")
                await send_with_typing(
                    message.channel,
                    lambda: message.channel.send("Oups, j'ai eu un petit bug interne."),
                )
                return

        # --- Si aucune des conditions n'est remplie ---
        await bot.process_commands(message)
