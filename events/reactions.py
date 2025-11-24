# events/reactions.py

import discord
from discord import RawReactionActionEvent
from utils.role_utils import get_role_mapping, get_role_cached # On suppose que ces imports sont bons

# Doit être asynchrone pour être chargé
async def setup(bot):
    
    @bot.event
    async def on_raw_reaction_add(payload: RawReactionActionEvent):
        # On vérifie que ce n'est pas le bot lui-même
        if payload.user_id == bot.user.id:
            return
            
        mapping = get_role_mapping(payload.message_id)
        if not mapping:
            return

        emoji = str(payload.emoji)
        if emoji not in mapping:
            return

        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return

        # On utilise fetch_member au lieu de get_member pour être sûr de l'avoir
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return # Le membre a quitté le serveur
        
        if not member or member.bot: # Double vérif
            return

        role = get_role_cached(guild, mapping[emoji])
        if role:
            try:
                await member.add_roles(role, reason="Rôle ajouté par réaction")
            except discord.Forbidden:
                print(f"Permissions manquantes pour ajouter le rôle {role.name} à {member.name}")
            except Exception as e:
                print(f"Erreur on_raw_reaction_add : {e}")


    @bot.event
    async def on_raw_reaction_remove(payload: RawReactionActionEvent):
        # On vérifie que ce n'est pas le bot lui-même
        if payload.user_id == bot.user.id:
            return
            
        mapping = get_role_mapping(payload.message_id)
        if not mapping:
            return

        emoji = str(payload.emoji)
        if emoji not in mapping:
            return

        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return

        # Ici get_member est OK car le membre est *censé* être dans le cache
        # Mais fetch est plus sûr si le bot a redémarré
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return # Le membre a quitté le serveur

        if not member or member.bot:
            return

        role = get_role_cached(guild, mapping[emoji])
        if role:
            try:
                await member.remove_roles(role, reason="Rôle retiré par réaction")
            except discord.Forbidden:
                print(f"Permissions manquantes pour retirer le rôle {role.name} à {member.name}")
            except Exception as e:
                print(f"Erreur on_raw_reaction_remove : {e}")