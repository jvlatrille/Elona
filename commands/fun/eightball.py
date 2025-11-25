# commands/fun/eightball.py

import discord
from discord import app_commands
import random
from utils.typing_helper import send_with_typing

# L'import est correct par rapport à ton arborescence
from data.data import r8ball

# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="8ball",
        description="Pose une question à la boule magique."
    )
    @app_commands.describe(
        question="Ta question (mets un '?' sinon t'es débile)"
    )
    async def eightball_cmd(interaction: discord.Interaction, question: str):

        # check de base : faut un ?
        if not question.strip().endswith("?"): # .strip() enlève les espaces en trop
            return await send_with_typing(
                interaction.channel,
                lambda: interaction.response.send_message(
                    "Mets un `?` à la fin stp, sinon j’te réponds pas.",
                    ephemeral=True,
                ),
            )

        rep = random.choice(r8ball)

        embed = discord.Embed(
            title="🎱 Boule Magique",
            description=None,
            color=0x9400D3 # Bonne couleur !
        )

        # On met la question en "description" de l'embed, c'est plus joli
        embed.description = f"**Ta question :**\n*« {question} »*"

        # On met la réponse en "champ" principal
        embed.add_field(
            name="Ma réponse :",
            value=f"**{rep}**",
            inline=False
        )

        # On ajoute le nom et l'avatar de l'auteur
        embed.set_author(
            name=f"Demandé par {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await send_with_typing(interaction.channel, lambda: interaction.response.send_message(embed=embed))
