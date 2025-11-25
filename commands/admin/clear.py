# commands/admin/clear.py

import discord
from discord import app_commands

# commands/admin/clear.py

import discord
from discord import app_commands
import asyncio # Non nécessaire mais bonne pratique si on devait sleep ou attendre

# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="clear",
        description="Supprime un certain nombre de messages dans le salon."
    )
    @app_commands.describe(
        # On peut utiliser Range pour que Discord valide le nombre (entre 1 et 100)
        amount="Nombre de messages à supprimer (entre 1 et 100)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_cmd(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        
        # On répond tout de suite à Discord "ok je m'en occupe"
        await interaction.response.defer(ephemeral=False)

        try:
            # On purge le salon (attention: purge limite la suppression aux 14 derniers jours)
            deleted = await interaction.channel.purge(limit=amount)

            # On envoie la vraie réponse (en modifiant le message "thinking...")
            await interaction.followup.send(
                f"J’ai supprimé **{len(deleted)} messages**."
            )

        except discord.Forbidden:
            # Si le bot n'a pas la permission
            await interaction.followup.send(
                "J’ai pas les permissions pour supprimer des messages.",
                ephemeral=True
            )

        except Exception as e:
            # Gère le cas critique où l'interaction est trop vieille (404 Unknown Message)
            print(f"Erreur critique inattendue ou Timeout pour /clear: {e}")
            if interaction.response.is_done():
                 # Si l'interaction a expiré, on ne peut rien envoyer au client,
                 # la console reste le seul endroit où l'erreur est visible.
                 pass
            else:
                 # Si on peut encore répondre, on envoie un message d'erreur éphémère.
                 await interaction.response.send_message(
                    f"Erreur inattendue : `{e}`", 
                    ephemeral=True
                 )


    # --- Gestion de l'erreur de permission ---
    @clear_cmd.error
    async def on_clear_cmd_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gère les erreurs de permission pour la commande /clear"""
        
        if isinstance(error, app_commands.MissingPermissions):
            # Tu n'as pas la permission de gérer les messages.
            # On utilise .send_message car .defer n'a pas été appelé si la permission manque
            await interaction.response.send_message(
                "Tu n'as pas la permission de gérer les messages.",
                ephemeral=True
            )
        
        # RangeError n'existe pas. L'erreur de transformation est gérée par TransformerError
        elif isinstance(error, app_commands.TransformerError):
            # Gère l'erreur si l'utilisateur essaie de contourner le Range (très rare)
            await interaction.response.send_message(
                "Le nombre doit être entre 1 et 100.",
                ephemeral=True
            )
            
        else:
            # Gère les autres erreurs qui surviennent avant le defer (très rare)
            print(f"Erreur non gérée pour /clear : {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Une erreur est survenue.", ephemeral=True
                )
            else:
                # Cette partie est peu probable, car l'erreur critique est gérée au-dessus
                await interaction.followup.send(
                    "Une erreur est survenue.", ephemeral=True
                )