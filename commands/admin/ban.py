# commands/admin/ban.py

import discord
from discord import app_commands

# Doit être asynchrone pour être chargé par load_extension
async def setup(bot):

    @bot.tree.command(
        name="ban",
        description="Ban un membre du serveur."
    )
    @app_commands.describe(
        member="Le membre à bannir",
        reason="La raison du ban"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_cmd(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        
        # --- Vérifications initiales ---

        if member.id == interaction.client.user.id:
            return await interaction.response.send_message(
                "Je ne vais pas me ban moi-même fréro calme-toi.",
                ephemeral=True
            )

        if member.id == interaction.user.id:
            return await interaction.response.send_message(
                "Si tu veux t'auto-ban utilise /suicide",
                ephemeral=True
            )
            
        # --- Vérification de la hiérarchie ---
        
        if interaction.guild.me.top_role <= member.top_role:
            return await interaction.response.send_message(
                f"Je ne peux pas bannir {member.mention} car son rôle est plus élevé ou égal au mien.",
                ephemeral=True
            )
            
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(
                f"Tu ne peux pas bannir {member.mention} car son rôle est plus élevé ou égal au tien.",
                ephemeral=True
            )

        # --- Action ---

        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(
                f"{member.mention} a été banni.\nRaison : {reason}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Je n'ai pas la permission 'Bannir des membres' sur le serveur.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Erreur inattendue : {e}",
                ephemeral=True
            )

    # --- Gestion de l'erreur de permission ---
    # CE BLOC DOIT ÊTRE INDENTÉ (dans le setup)
    @ban_cmd.error
    async def on_ban_cmd_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gère les erreurs de permission pour la commande /ban"""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Tu n'as pas la permission de bannir des membres.",
                ephemeral=True
            )
        else:
            print(f"Erreur non gérée pour /ban : {error}")
            await interaction.response.send_message(
                "Une erreur est survenue lors de l'exécution de la commande.",
                ephemeral=True
            )