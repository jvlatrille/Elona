# commands/admin/clear.py

import discord
from discord import app_commands

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
        # Le "ephemeral=False" ici veut dire que le message "Bot is thinking..."
        # sera public et sera *modifié* par le followup. C'est bien !
        await interaction.response.defer(ephemeral=False)

        try:
            # on purge le salon
            deleted = await interaction.channel.purge(limit=amount)

            # puis on envoie la vraie réponse (en modifiant le message "thinking...")
            await interaction.followup.send(
                f"J’ai supprimé **{len(deleted)} messages**."
                # ephemeral=False est implicite car le defer était False
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "J’ai pas les permissions pour supprimer des messages.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"Erreur inattendue : `{e}`",
                ephemeral=True
            )

    # --- Gestion de l'erreur de permission ---
    @clear_cmd.error
    async def on_clear_cmd_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gère les erreurs de permission pour la commande /clear"""
        if isinstance(error, app_commands.MissingPermissions):
            # Utilise .send_message car .defer n'a pas été appelé si la permission manque
            await interaction.response.send_message(
                "Tu n'as pas la permission de gérer les messages.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.RangeError):
            # Gère l'erreur si l'utilisateur essaie de contourner le Range
            await interaction.response.send_message(
                f"Le nombre doit être entre 1 et 100. Tu as donné {error.value}.",
                ephemeral=True
            )
        else:
            print(f"Erreur non gérée pour /clear : {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Une erreur est survenue.", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "Une erreur est survenue.", ephemeral=True
                )