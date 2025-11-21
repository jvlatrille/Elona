from email import message
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import random
import re
import requests
import logging
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from discord import app_commands

from cachetools import TTLCache

# === IMPORTS PROJET ===
import data
import confidentiel
from openai import OpenAI



# Installation automatique des packages requis
def install_requirements():
    # On récupère le chemin absolu du répertoire où se trouve le script actuel
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(current_dir, "requirements.txt")

    if os.path.exists(requirements_path):
        try:
            print("Installation des dépendances...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", requirements_path]
            )
            print("Installation terminée.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation des dépendances: {e}")
            sys.exit(1)
    else:
        print("Erreur : Le fichier requirements.txt est introuvable.")
        sys.exit(1)


install_requirements()

# Configuration de logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s : %(message)s",  # Format personnalisé pour inclure l'heure et le message
    datefmt="%Y-%m-%d %H:%M:%S",  # Format de la date
)

prefix = "/"
bot = commands.Bot(
    command_prefix=prefix, description="Bot de dév", intents=discord.Intents.all()
)

client_ai = OpenAI(api_key=confidentiel.OPENAI_API_KEY)

historiques_salons = {}

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_GENERAL = load_prompt("prompts/prompt_general.txt")
PROMPT_ELONA   = load_prompt("prompts/prompt_elona.txt")
def init_history(prompt=PROMPT_GENERAL):
    return [{"role": "system", "content": prompt}]

def add_to_history(channel_id, role, content):
    if channel_id not in historiques_salons:
        historiques_salons[channel_id] = init_history()
    historiques_salons[channel_id].append({"role": role, "content": content})


async def generate_reply(channel_id):
    msgs = historiques_salons.get(channel_id, init_history())
    msgs = msgs[-10:]

    msgs.append({
        "role": "system",
        "content": "Réponds toujours quelque chose, même si le message reçu est très court."
    })

    try:
        res = client_ai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=msgs,
            max_completion_tokens=200,
            temperature=0.7,
            frequency_penalty=0.2,
            presence_penalty=0.1,
        )
    except Exception as e:
        print("Erreur OpenAI :", e)
        return "ptdr le cerveau m'a lâché deux secondes"

    txt = res.choices[0].message.content
    if not txt or txt.strip() == "":
        txt = "ptdr j'ai bugué deux secondes"

    add_to_history(channel_id, "assistant", txt)
    return txt

def log_command_usage(user, command_name, arguments=""):
    print(
        f"User {user} a exécuté la commande: {command_name} avec les arguments: {arguments}"
    )


# Infos du bot
@bot.event
async def on_ready():
    print("Connecté")
    try:
        synced = await bot.tree.sync()
        print(f"Synchronized {len(synced)} commands")
    except Exception as e:
        print(e)

    user = bot.get_user(583268098983985163) # Mon id discord

    if user:
        try:
            await user.send("Salut")
            print("Message envoyé à l'hote")
        except discord.Forbidden:
            print(f"Impossible d'envoyer un message à l'utilisateur avec l'ID 583268098983985163 (10RD)")

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.playing, name="Still cooking..."
        ),
    )


@bot.event
async def on_message(message):
    # ---------------------------------------------------------
    # 0) IGNORER LES BOTS
    # ---------------------------------------------------------
    if message.author.bot:
        return
    
    content = message.content.lower() # Récup du message

    # ---------------------------------------------------------
    # 1) IA : DM (toujours actif)
    # ---------------------------------------------------------
    if isinstance(message.channel, discord.DMChannel):
        contenu_user = message.content

        if message.attachments:
            contenu_user += " (note : l’utilisateur a envoyé une pièce jointe, je ne peux pas la lire)"

        add_to_history(message.author.id, "user", contenu_user)
        async with message.channel.typing():
            rep = await generate_reply(message.author.id)
        return await message.channel.send(rep)

    # ---------------------------------------------------------
    # 2) IA : salons autorisés sur serveur cible
    # ---------------------------------------------------------
    if message.guild and message.guild.id == confidentiel.SERVEUR_CIBLE:
        if not confidentiel.SALONS_AUTORISES or message.channel.id in confidentiel.SALONS_AUTORISES:
            contenu_user = message.content

            if message.attachments:
                contenu_user += " (note : l’utilisateur a envoyé une pièce jointe, je ne peux pas la lire)"

            add_to_history(message.channel.id, "user", contenu_user)

            async with message.channel.typing():
                rep = await generate_reply(message.channel.id)
            return await message.channel.send(rep)

    # Mention SEULE du bot
    if (
        bot.user in message.mentions
        and len(message.mentions) == 1
        and message.content.strip() == f"<@{bot.user.id}>"
    ):
        command_list = [
            f"{command.name}: {command.description}\n"
            for command in bot.tree.walk_commands()
        ]
        embed = discord.Embed(title="Liste des commandes :", color=0x00FFFF)
        sans_admin = [command for command in command_list if "[admin]" not in command]
        commandes = "\n".join(sans_admin)
        embed.add_field(name="A utiliser avec '/'", value=commandes, inline=False)

        await message.reply(
            f"{random.choice(data.salutations)} {message.author.display_name}\n{data.listeCommandes}\n",
            embed=embed,
        )

    # salutations
    if content in {s.lower() for s in data.salutations}:
        await message.reply(
            f"{random.choice(data.salutations)} {message.author.display_name} \n{random.choice(data.politesse)} ?"
        )


    # "et toi"
    if bot.user.mentioned_in(message) and "et toi" in message.content.lower():
        await message.reply(
            "Je suis un bot.\nTant que ma connexion est bonne, je suis heureux (ce n'est pas le cas actuellement)."
        )

    # racisme
    racistes = [m for m in data.listeMotRacistes if m.lower() in content]

    if racistes:
        if len(racistes) >= 2:
            await message.reply(f"Tu es très raciste {message.author.display_name} >:(")
        else:
            await message.reply(
                f"Je crois que tu es raciste {message.author.display_name} (c'est mal)"
            )


    # ban threat
    for mot in data.bannedContent:
        if mot.lower() in message.content.lower():
            gifToSend = random.choice(data.attention)
            embed = discord.Embed()
            embed.set_image(url=gifToSend)
            await message.reply(
                f"La prochaine fois c'est le ban {message.author.display_name}, tu es méchant"
            )
            await message.reply(embed=embed)
            return

    # quoi / feur
    if re.search(r"\bquoi\b", message.content.lower().strip(" .,!?")):
        await message.reply(random.choice(data.feur))

    # nice / noice
    if "nice" in message.content.lower() or "noice" in message.content.lower():
        await message.reply("https://media1.tenor.com/m/H6sjheSkU1wAAAAC/noice-nice.gif")

    # ---------------------------------------------------------
    # 4) TRAITEMENT DES COMMANDES
    # ---------------------------------------------------------
    await bot.process_commands(message)




@bot.event
async def on_command(ctx):
    command_name = ctx.command.name
    user = ctx.author
    arguments = " ".join(ctx.args[1:]) if len(ctx.args) > 1 else "Aucun argument"

    # Création du message de log personnalisé
    log_message = (
        f" {user.name}, id : {user.id}\n"
        f"A exécuté la commande: {command_name} avec les arguments: {arguments}\n"
    )

    # Log du message
    logging.info(log_message)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        command_name = interaction.command.name if interaction.command else "inconnue"
        user = interaction.user

        # Création du message de log personnalisé
        log_message = (
            f" {user.name}, id: {user.id}\n"
            f"A exécuté la commande slash: {command_name}\n"
        )

        # Log du message
        logging.info(log_message)


# Message de bienvenue
@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title="Bienvenue",
            description=f"Bienvenue à {member.mention} sur le serveur !",
            color=discord.Color.green(),
        )
        embed.set_image(url=random.choice(data.gifBienvenue))
        await channel.send(embed=embed)


"""
COMMANDES /
"""
@bot.tree.command(name="elona", description="Analyse la discussion du salon avec la personnalité Elona")
async def elona_command(interaction: discord.Interaction):
    channel = interaction.channel
    channel_id = channel.id

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)

    messages = []
    async for msg in channel.history(limit=200):
        if msg.created_at < cutoff:
            break
        if msg.author.id == bot.user.id:
            continue
        if msg.content:
            messages.append(msg)

    # reset hist perso
    historiques_salons[channel_id] = init_history(PROMPT_ELONA)

    for m in reversed(messages[-30:]):
        add_to_history(channel_id, "user", m.content)

    await interaction.response.defer()
    async with channel.typing():
        rep = await generate_reply(channel_id)

    await interaction.edit_original_response(content=rep)

# Commande de ping
@bot.tree.command(name="ping", description="Retour de la latence du bot")
async def ping(interaction: discord.Interaction):
    gif_url = random.choice(data.gifCringe)
    embed = discord.Embed()
    embed.set_image(url=gif_url)
    await interaction.response.send_message(
        f"Mon temps de traitement est de {bot.latency} secondes \n C'est un peu lent, je sais :confounded::point_right::point_left: \n||c'est génant comme message mais c'est drôle||",
        embed=embed,
    )


# Commande de ping sans gif
@bot.tree.command(name="pings", description="Ping sans gif")
async def pings(interaction: discord.Interaction):
    await interaction.response.send_message(f"Temps de traitement : {bot.latency} s")


# Commande de ban
@bot.tree.command(name="ban", description="Bans un membre")
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(interaction, member: discord.Member, reason: str):
    try:
        if member.id == bot.user.id:  # Vérifiez si le membre à bannir est le bot
            await interaction.response.send_message(
                "EH! J'ai rien fait moi... Je suis encore rejeté par la société sûrement... :("
            )

        elif member.id == interaction.user.id:
            await interaction.response.send_message(
                "Mais t'es con ? Utilise la commande suicide pour faire ça!"
            )
        else:
            if reason is None:
                reason = f"None provided by {interaction.user.name}"
            await member.ban(reason=reason)
            await interaction.response.send_message(
                f"{interaction.user.mention}, {member.mention} a bien été ban!\n\nRaison: {reason}"
            )
    except commands.MissingPermissions as e:
        await interaction.response.send_message(
            f"Tu n'as pas les permissions requises pour kick quelqu'un: {e}"
        )
    except discord.Forbidden as e:
        await interaction.response.send_message(
            f"Je suis pauvre, je n'ai pas les permissions de faire ça : {e}"
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Oups... y'a une couille dans le potage : {e}"
        )


# Commande de suicide
@bot.tree.command(
    name="suicide", description="Mdr tu te suicide (perma ban de toi même miskine)"
)
@commands.has_permissions(ban_members=True, administrator=True)
async def suicide(interaction, member: discord.Member):
    try:
        if member.id == member.id:
            await member.ban(reason=None)
            await interaction.response.send_message(
                f"{interaction.user}, s'est suicidé"
            )
        else:
            await interaction.response.send_message(
                "Tu ne peux pas suicider quelqu'un d'autre !"
            )
    except commands.MissingPermissions as e:
        await interaction.response.send_message(
            f"Tu n'as pas les permissions requises pour kick quelqu'un: {e}"
        )
    except discord.Forbidden as e:
        await interaction.response.send_message(
            f"Je suis pauvre, je n'ai pas les permissions de faire ça : {e}"
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Oups... y'a une couille dans le potage : {e}"
        )


# Commande de unban
@bot.tree.command(
    name="unban", description="C'est comme ban quelqu'un mais en sens inverse"
)
async def unban(ctx, user: discord.User, reason: str = "Aucune raison spécifiée"):
    # Vérifier si l'utilisateur a la permission de débannir des membres
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("Vous n'avez pas la permission de débannir des membres.")
        return

    # Vérifier si la cible est bien bannie
    banned_users = await ctx.guild.bans()

    if user not in banned_users:
        await ctx.send(f"L'utilisateur {user} n'est pas banni.")
        return
    else:
        # Débannir l'utilisateur
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"{user} a été débanni.")


# Commande de kick
@bot.tree.command(name="kick", description="Dégager une personne fortement chiante")
async def kick(ctx, user: discord.User):
    await ctx.guild.kick(user)
    await ctx.send(
        f"{user} a été expulsé tah les migrants (ah non).\n||c'est pas très très gentil de dire ça||"
    )


# Commande de clear
@bot.tree.command(
    name="clear", description="Clear un nombre choisi de messages dans la conversation"
)
async def clear(ctx, amount: int):
    # On va éviter de planter les serveurs de replit, et ton Xiaomi poubelle <- tg
    if amount > 50:
        await ctx.send(f"Tu ne peux pas supprimer autant de messages")
    else:
        async for message in ctx.channel.history(limit=amount):
            await message.delete()
        return


# Commande de gifs
@bot.tree.command(name="gif", description="Envoyer un gif")
async def gif(interaction: discord.Interaction):
    gifToSend = random.choice(data.listeGifs)
    embed = discord.Embed()
    embed.set_image(url=gifToSend)
    await interaction.response.send_message(embed=embed)


# Commande de giflist
@bot.tree.command(name="giflist", description="[admin] : Envoyer la liste des gifs")
async def giflist(interaction: discord.Interaction):
    """if interaction.user.id != data.listeDesAdmins.values():
    await interaction.channel.send(
        "Vous n'êtes pas autorisé à exécuter cette commande.")
    return"""
    for gif in data.listeGifs:
        embed = discord.Embed()
        embed.set_image(url=gif)
        await interaction.channel.send(embed=embed)
    await interaction.channel.send(f"Il y a {len(data.listeGifs)} gifs dans la liste")

# Commande restore
@bot.tree.command(
    name="restore", description="Restaure les noms de salons depuis un moment donné"
)
@app_commands.describe(
    minutes="Nombre de minutes dans le passé (max 2880)"
)
async def restore(interaction: discord.Interaction, minutes: int):
    if minutes <= 0 or minutes > 2880:
        await interaction.response.send_message(
            "Le nombre de minutes doit être compris entre 1 et 2880.",
            ephemeral=True,
        )
        return

    restore_from = discord.utils.utcnow() - timedelta(minutes=minutes)

    count = 0
    async for entry in interaction.guild.audit_logs(
        action=discord.AuditLogAction.channel_update,
        after=restore_from,
        oldest_first=False,
    ):
        channel = entry.target
        before = entry.before
        if (
            isinstance(channel, discord.abc.GuildChannel)
            and before
            and before.name
        ):
            try:
                await channel.edit(
                    name=before.name,
                    reason=f"Restore command by {interaction.user}",
                )
                count += 1
            except discord.Forbidden:
                continue

    formatted = restore_from.strftime("%Y-%m-%d %H:%M UTC")
    await interaction.response.send_message(
        f"Restauration terminée depuis {formatted}. {count} salon(s) modifié(s).",
        ephemeral=True,
    )



# Commande 8ball
@bot.tree.command(name="8ball", description='Posez une question à la "boule magique"')
async def eight_ball(interaction: discord.Interaction, *, question: str):
    if question.endswith("?"):
        response = random.choice(data.r8ball)
        embed = discord.Embed(
            title="Boule Magique (Wallah c'est vrai)", description=None, color=0x9400D3
        )
        embed.add_field(
            name=f"Question de {interaction.user}", value=question, inline=False
        )
        embed.add_field(name="Réponse", value=response, inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            "Apprend à écrire :/\nGénéralement on met un point d'interrogation à la fin des questions.\nSi tu ne sais pas comment faire, voila un exemple :\n```Est tu débile ???????????```"
        )


# Commande pour générer une image à partir du texte
@bot.tree.command(
    name="image_generation",
    description="Générer une image avec un texte donné (mais en anglais (mais c'est gratuit))",
)
async def image_generation(interaction: discord.Interaction, *, demande: str):
    # Envoyer un message pour indiquer que la demande est prise en compte
    await interaction.response.send_message(f"Demande prise en compte : {demande}")

    # Retirer les caractères spéciaux et remplacer les espaces par des '%20'
    texte_final = re.sub(r"[^\w\s]", "", demande)
    texte_final = texte_final.replace(" ", "%20")
    # Créer l'URL de l'image
    image_url = f"https://image.pollinations.ai/prompt/{texte_final}.png"
    # Créer l'embed avec l'URL de l'image
    embed = discord.Embed()
    embed.set_image(url=image_url)
    # Envoyer l'embed
    await interaction.channel.send(embed=embed)


def search_anime(name):
    try:
        query = """
        query ($name: String) {
            Media (search: $name, type: ANIME) {
                id
                title { romaji }
                coverImage { large }
            }
        }
        """
        variables = {"name": name}
        url = "https://graphql.anilist.co"
        response = requests.post(url, json={"query": query, "variables": variables}, timeout=5)
        data = response.json()

        media = data.get("data", {}).get("Media")
        if media:
            return data, media["title"]["romaji"]

    except Exception as e:
        print("Erreur AniList:", e)

    return None, None



@bot.tree.command(name="anime", description="Donne un lien vers un anime")
async def anime(interaction, nom_anime: str, plateforme: str = None):
    anime_data, precise_name = search_anime(nom_anime)
    if not precise_name:
        await interaction.response.send_message("Aucun anime trouvé avec ce nom.")
        return

    plateformes = {
        "voiranime": "https://v5.voiranime.com/anime/",
        "animesama": "https://anime-sama.fr/catalogue/",
        "animeplanet": "https://www.anime-planet.com/anime/all?name=",
        "otakufr": "https://otakufr.cc/toute-la-liste-affiches/?q=",
        "gumgum streaming": "https://gum-gum-streaming.com/",
        "9anime": "https://9animetv.to/search?keyword=",
        "animevostfr": "https://animevostfr.tv/?s=",
        "mavanimes": "https://www.mavanimes.co/?s=",
    }
    embed = discord.Embed(title=f"Liens pour {precise_name}", color=0x1E88E5)

    if plateforme:
        plateforme = plateforme.lower()
        if plateforme not in plateformes:
            await interaction.response.send_message("Plateforme non prise en charge")
            return
        url_complet = (
            f"{plateformes[plateforme]}{precise_name.lower().replace(' ', '-')}/"
        )
        embed.add_field(
            name=f"{plateforme.capitalize()}",
            value=f"[{precise_name}]({url_complet})",
            inline=False,
        )
    else:
        for plat, base_url in plateformes.items():
            url_complet = f"{base_url}{precise_name.lower().replace(' ', '-')}/"
            embed.add_field(
                name=f"{plat.capitalize()}",
                value=f"[{precise_name}]({url_complet})",
                inline=False,
            )

    # Optionally add image if available
    anime_cover = anime_data["data"]["Media"]["coverImage"]["large"]
    if anime_cover:
        embed.set_image(url=anime_cover)

    await interaction.response.send_message(
        f"Anime demandé : {nom_anime}\n", embed=embed
    )


# Commande pour attribuer des rôles via des réactions
@bot.tree.command(name="roleattribution", description="Attribution de rôles")
@app_commands.checks.has_permissions(administrator=True)
async def roleattribution(
    interaction: discord.Interaction, message: str, color: str, roles: str
):
    roles_list = [role.strip() for role in roles.split()]
    guild = interaction.guild

    # Conversion de la couleur française en hexadécimal
    color_hex = data.color_dict.get(color.lower())
    if color_hex is None:
        await interaction.response.send_message(
            "Couleur invalide. Utilisez une couleur en français, par exemple 'rouge', 'bleu', etc.",
            ephemeral=True,
        )
        return
    embed_color = discord.Color(color_hex)

    # Vérification et récupération des rôles mentionnés
    valid_roles = []
    role_ids = [
        int(role_id.strip("<@&>"))
        for role_id in roles_list
        if role_id.strip("<@&>").isdigit()
    ]
    for role_id in role_ids:
        role = discord.utils.get(guild.roles, id=role_id)
        if role:
            valid_roles.append(role)
        else:
            await interaction.response.send_message(
                f"Rôle mentionné non trouvé", ephemeral=True
            )
            return

    # Création de l'embed
    embed = discord.Embed(
        title="Attribution de rôles", description=message, color=embed_color
    )
    emoji_list = [
        "🔴",
        "🟠",
        "🟡",
        "🟢",
        "🔵",
        "🟣",
        "🟤",
    ]  # Liste d'émojis prédéfinis (à étendre si nécessaire)

    if len(valid_roles) > len(emoji_list):
        await interaction.response.send_message(
            "Trop de rôles pour les émojis disponibles", ephemeral=True
        )
        return

    emoji_role_dict = {}
    for i, role in enumerate(valid_roles):
        embed.add_field(
            name=f"Rôle {role.name}",
            value=f"Réagissez avec {emoji_list[i]}",
            inline=False,
        )
        emoji_role_dict[emoji_list[i]] = role

    # Envoi de l'embed et ajout des réactions
    bot_message = await interaction.channel.send(embed=embed)
    for emoji in emoji_role_dict:
        await bot_message.add_reaction(emoji)

    # Sauvegarde de l'ID du message et des rôles associés (exemple basique, à améliorer pour une persistance)
    role_message_data[bot_message.id] = emoji_role_dict
    await interaction.response.send_message(
        "Message de rôle créé avec succès", ephemeral=True
    )


# Dictionnaire pour stocker les messages de rôle et leurs associations emoji-rôle
role_message_data = {}


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id in role_message_data:
        guild = bot.get_guild(payload.guild_id)
        role = role_message_data[payload.message_id].get(str(payload.emoji))
        if role:
            member = guild.get_member(payload.user_id)
            await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in role_message_data:
        guild = bot.get_guild(payload.guild_id)
        role = role_message_data[payload.message_id].get(str(payload.emoji))
        if role:
            member = guild.get_member(payload.user_id)
            await member.remove_roles(role)


# Cache pour les données de rôle, expirant après 1 heure
role_cache = TTLCache(maxsize=100, ttl=3600)


def fetch_role(guild, role_id):
    return guild.get_role(role_id)

def get_role_from_cache(guild, role_id):
    role = role_cache.get(role_id)
    if not role:
        role = fetch_role(guild, role_id)
        if role:
            role_cache[role_id] = role
    return role



# Gestion d'erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(
            "Une erreur s'est produite lors de l'exécution de votre commande."
        )
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Cette commande est en cooldown. Réessayez dans {error.retry_after:.2f} secondes."
        )


bot.run(confidentiel.TOKENELONA)
