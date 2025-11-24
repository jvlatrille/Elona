# commands/general/image_generation.py

import discord
from discord import app_commands
import urllib.parse


# Doit être asynchrone pour être chargé
async def setup(bot):

    @bot.tree.command(
        name="image_generation",
        description="Génère une image à partir d’une description (en anglais)."
    )
    @app_commands.describe(
        demande="Description de l’image à générer"
    )
    async def image_generation_cmd(interaction: discord.Interaction, demande: str):

        # IMPORTANT : On 'defer' car l'API peut être lente
        await interaction.response.defer()

        # Nettoyer le prompt
        prompt_propre = demande.strip()

        # On encode proprement la description
        # 'quote' est plus adapté pour un chemin d'URL que 'quote_plus'
        description_encoded = urllib.parse.quote(prompt_propre)

        # URL Pollinations
        image_url = f"https://image.pollinations.ai/prompt/{description_encoded}"
        # Note: tu peux ajouter des params, ex: image_url += "?width=1024&height=1024"

        embed = discord.Embed(
            title="Image générée",
            description=f"Prompt : **{prompt_propre}**",
            color=0x7289DA
        )
        embed.set_image(url=image_url)
        embed.set_footer(text="Généré via Pollinations.ai")

        # On utilise .followup.send() car on a 'defer' la réponse
        await interaction.followup.send(embed=embed)