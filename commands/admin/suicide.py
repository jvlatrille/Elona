import discord
from discord import app_commands

# Doit être asynchrone pour être chargé par le bot
async def setup(bot):

    @bot.tree.command(
        name="suicide",
        description="Tu te bannis toi-même du serveur (auto-ban)."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def suicide_cmd(interaction: discord.Interaction):

        user = interaction.user

        # sécurité : ne jamais bannir le bot
        if user.id == interaction.client.user.id:
            return await interaction.response.send_message(
                "Frérot… je vais pas me suicider moi-même.",
                ephemeral=True
            )

        # Tentative de ban
        try:
            await interaction.guild.ban(
                user,
                reason="Auto-ban via commande /suicide"
            )

            await interaction.response.send_message(
                f"{user.mention} s’est **auto-banni** du serveur.\n"
                "Un champion incontesté."
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "J’ai pas les perms pour te bannir. T’es plus fort que moi.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"Erreur inattendue : {e}",
                ephemeral=True
            )