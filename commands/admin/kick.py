# commands/admin/kick.py

import discord
from discord import app_commands

# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="kick",
        description="Expulse un membre du serveur."
    )
    @app_commands.describe(
        member="La personne à expulser",
        reason="La raison du kick"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_cmd(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison fournie"):
        
        # --- Vérifications initiales ---

        # Impossible de kick le bot
        if member.id == interaction.client.user.id:
            return await interaction.response.send_message(
                "Tu veux m’expulser moi ? tranquille l’artiste.",
                ephemeral=True
            )

        # Impossible de se kick soi-même
        if member.id == interaction.user.id:
            return await interaction.response.send_message(
                "Si tu veux te virer, fais /suicide frérot.",
                ephemeral=True
            )
            
        # --- Vérification de la hiérarchie (IMPORTANT) ---
        
        # Vérifie si le bot peut kick (rôle plus haut)
        if interaction.guild.me.top_role <= member.top_role:
            return await interaction.response.send_message(
                f"Je ne peux pas expulser {member.mention} car son rôle est plus élevé ou égal au mien.",
                ephemeral=True
            )
            
        # Vérifie si l'utilisateur peut kick (rôle plus haut)
        if interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message(
                f"Tu ne peux pas expulser {member.mention} car son rôle est plus élevé ou égal au tien.",
                ephemeral=True
            )

        # --- Action ---

        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                f"{member.mention} a été expulsé.\nRaison : {reason}"
            )

        except discord.Forbidden:
            # Géré par la hiérarchie, mais au cas où (si le bot n'a pas la perm globale)
            await interaction.response.send_message(
                "Je n'ai pas la permission 'Expulser des membres' sur le serveur.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Erreur inattendue : {e}",
                ephemeral=True
            )

    # --- Gestion de l'erreur de permission ---
    @kick_cmd.error
    async def on_kick_cmd_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gère les erreurs de permission pour la commande /kick"""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Tu n'as pas la permission d'expulser des membres.",
                ephemeral=True
            )
        else:
            print(f"Erreur non gérée pour /kick : {error}")
            await interaction.response.send_message(
                "Une erreur est survenue lors de l'exécution de la commande.",
                ephemeral=True
            )