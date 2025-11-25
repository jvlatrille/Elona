# commands/admin/unban.py

import discord
from discord import app_commands
from utils.typing_helper import send_with_typing

# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="unban",
        description="Débannir un utilisateur à partir de son ID."
    )
    @app_commands.describe(
        user_id="L’ID de l’utilisateur à débannir",
        reason="Raison du débannissement"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_cmd(
        interaction: discord.Interaction,
        user_id: str,
        reason: str = "Aucune raison fournie"
    ):
        guild = interaction.guild

        # --- 1. Validation de l'ID ---
        try:
            user_id_int = int(user_id)
        except ValueError:
            return await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Format invalide. Donne un ID numérique.",
                    ephemeral=True,
                ),
            )

        # --- 2. Récupération du ban (méthode optimisée) ---
        try:
            # On cherche *spécifiquement* cet ID dans les bans
            # ban_entry contient .user et .reason
            ban_entry = await guild.get_ban(user_id_int)

        except discord.NotFound:
            # L'ID n'est pas dans la liste des bans
            return await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Cet utilisateur n’est pas (ou plus) dans la liste des bannis.",
                    ephemeral=True,
                ),
            )
        except discord.Forbidden:
            # Le bot n'a pas la permission de voir la liste des bans
            return await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Je n’ai pas les permissions pour voir les utilisateurs bannis.",
                    ephemeral=True,
                ),
            )
        except Exception as e:
            return await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    f"Erreur lors de la récupération du ban : {e}",
                    ephemeral=True,
                ),
            )

        # --- 3. Action de débannissement ---
        try:
            # On utilise l'objet utilisateur trouvé dans ban_entry
            await guild.unban(ban_entry.user, reason=reason)

            await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    f"**{ban_entry.user}** (ID: `{user_id_int}`) a été débanni.\nRaison : {reason}"
                ),
            )

        except discord.Forbidden:
            await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Impossible de le débannir (permissions insuffisantes).",
                    ephemeral=True,
                ),
            )
        except Exception as e:
            await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    f"Erreur inattendue : {e}",
                    ephemeral=True,
                ),
            )

    # --- Gestion de l'erreur de permission ---
    @unban_cmd.error
    async def on_unban_cmd_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gère les erreurs de permission pour la commande /unban"""
        if isinstance(error, app_commands.MissingPermissions):
            await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Tu n'as pas la permission 'Bannir des membres' (requise pour débannir).",
                    ephemeral=True,
                ),
            )
        else:
            print(f"Erreur non gérée pour /unban : {error}")
            await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Une erreur est survenue lors de l'exécution de la commande.",
                    ephemeral=True,
                ),
            )
