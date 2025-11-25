# commands/general/anime.py

import discord
from discord import app_commands
from urllib.parse import quote_plus # Pour formater les URL (ex: "One Piece" -> "One+Piece")
from utils.typing_helper import send_with_typing

# On importe la nouvelle version async
from utils.anime_utils import search_anime

# --- NOUVELLE STRUCTURE POUR LES PLATEFORMES ---
# On doit savoir si le site utilise une 'query' (?s=) ou un 'path' (/.../)
PLATEFORMES = {
    "voiranime":   {"base_url": "https://v5.voiranime.com/anime/", "type": "path"},
    "animesama":   {"base_url": "https://anime-sama.fr/catalogue/", "type": "path"},
    "animeplanet": {"base_url": "https://www.anime-planet.com/anime/all?name=", "type": "query"},
    "otakufr":     {"base_url": "https://otakufr.cc/toute-la-liste-affiches/?q=", "type": "query"},
    "gumgum":      {"base_url": "https://gum-gum-streaming.com/", "type": "home"}, # Cas spécial
    "9anime":      {"base_url": "https://9animetv.to/search?keyword=", "type": "query"},
    "animevostfr": {"base_url": "https://animevostfr.tv/?s=", "type": "query"},
    "mavanimes":   {"base_url": "https://www.mavanimes.co/?s=", "type": "query"},
}

# --- Fonction helper pour créer le bon lien ---
def get_link(platform_data, name_romaji):
    search_type = platform_data["type"]
    base_url = platform_data["base_url"]

    if search_type == "path":
        # 'One Piece' -> 'one-piece'
        kebab_name = name_romaji.lower().replace(" ", "-")
        return base_url.rstrip('/') + f"/{kebab_name}"

    if search_type == "query":
        # 'One Piece' -> 'One+Piece'
        query_name = quote_plus(name_romaji)
        return base_url + query_name

    if search_type == "home":
        return base_url # Juste la page d'accueil

    return None

# Doit être asynchrone pour être chargé
async def setup(bot):

    # --- Amélioration : Utiliser 'Choices' pour la plateforme ---
    platform_choices = [
        app_commands.Choice(name=name.capitalize(), value=name)
        for name in PLATEFORMES.keys()
    ]

    @bot.tree.command(
        name="anime",
        description="Cherche un anime et te donne les liens streaming."
    )
    @app_commands.describe(
        nom_anime="Nom de l'anime à chercher",
        plateforme="(Optionnel) Plateforme spécifique"
    )
    # L'utilisateur verra une liste déroulante des plateformes
    @app_commands.choices(plateforme=platform_choices)
    async def anime_cmd(
        interaction: discord.Interaction,
        nom_anime: str,
        plateforme: app_commands.Choice[str] = None # Type mis à jour
    ):
        await interaction.response.defer()

        # recherche AniList (maintenant avec 'await')
        info = await search_anime(nom_anime)
        if not info:
            return await send_with_typing(
                interaction.channel,
                lambda: interaction.followup.send(
                    f"Aucun anime trouvé pour `{nom_anime}`.",
                    ephemeral=True
                ),
            )

        precise_name = info["name"] # Le nom Romaji (ex: "One Piece")
        cover = info["cover"]

        embed = discord.Embed(
            title=f"Liens pour {precise_name}",
            description=f"_(Résultat pour `{nom_anime}` via AniList)_",
            color=0x1E88E5
        )

        # cas où l’utilisateur veut une plateforme précise
        if plateforme:
            # plateforme.value contient le nom (ex: "animesama")
            p_name = plateforme.value
            p_data = PLATEFORMES[p_name]

            link = get_link(p_data, precise_name)

            embed.description += f"\n\n[**Chercher sur {plateforme.name}**]({link})"

        else:
            # toutes les plateformes
            links_list = []
            for p_name, p_data in PLATEFORMES.items():
                link = get_link(p_data, precise_name)
                links_list.append(f"[{p_name.capitalize()}]({link})")

            # C'est plus propre de les mettre dans la description
            embed.description += "\n\n" + " | ".join(links_list)

        # image AniList
        if cover:
            embed.set_thumbnail(url=cover) # set_thumbnail est mieux pour les liens

        await send_with_typing(interaction.channel, lambda: interaction.followup.send(embed=embed))
