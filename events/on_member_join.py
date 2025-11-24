# events/on_member_join.py

import discord
import data.data as data
import random  # Ajout de random pour choisir un gif

# Doit être asynchrone pour être chargé
async def setup(bot):
    
    @bot.event
    async def on_member_join(member: discord.Member): # C'est bien de typer l'argument
        
        # Ignorer les bots
        if member.bot:
            return

        # 'system_channel' est le salon où Discord envoie les messages par défaut
        # (ex: "Jules a rejoint le serveur.")
        ch = member.guild.system_channel
        
        # On vérifie que ce salon existe et que le bot peut y écrire
        if ch and ch.permissions_for(member.guild.me).send_messages:
            embed = discord.Embed(
                title=f"Un nouveau membre est arrivé !",
                description=f"Bienvenue sur le serveur, {member.mention} !",
                color=discord.Color.green()
            )
            
            # Si data.gifBienvenue est une liste, on en prend un au hasard
            try:
                if data.gifBienvenue: # On vérifie que la liste existe et n'est pas vide
                    gif_url = random.choice(data.gifBienvenue)
                    embed.set_image(url=gif_url)
            except Exception as e:
                print(f"Erreur lors du choix du gif de bienvenue : {e}")

            # On ajoute l'avatar du membre, c'est plus sympa
            embed.set_thumbnail(url=member.display_avatar.url)
            
            try:
                await ch.send(embed=embed)
            except discord.Forbidden:
                print(f"Permissions manquantes pour envoyer le message de bienvenue dans {ch.name}")
            except Exception as e:
                print(f"Erreur envoi message bienvenue : {e}")