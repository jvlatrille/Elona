# commands/fun/gif.py

import discord
from discord import app_commands
import random

from data.data import listeGifs

# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="gif",
        description="Envoie un gif aléatoire."
    )
    async def gif_cmd(interaction: discord.Interaction):

        gif_url = random.choice(listeGifs)

        # Ajout d'une couleur et d'un titre (optionnel mais plus propre)
        embed = discord.Embed(
            title="Voici un gif !",
            color=discord.Color.blue() # Tu peux changer la couleur
        )
        embed.set_image(url=gif_url)

        await interaction.response.send_message(embed=embed)