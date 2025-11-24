# commands/general/ping.py
import discord
from discord import app_commands

# La fonction DOIT être asynchrone pour load_extension
async def setup(bot):

    @bot.tree.command(
        name="ping",
        description="Affiche la latence du bot."
    )
    async def ping_cmd(interaction: discord.Interaction):

        latence = round(interaction.client.latency * 1000)  # en ms

        embed = discord.Embed(
            title="Pong",
            description=f"Latence : **{latence} ms**",
            color=0x00AEEF
        )

        await interaction.response.send_message(embed=embed)