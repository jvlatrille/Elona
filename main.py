import random
import discord
from discord.ext import commands
from discord import app_commands
from discord import Guild
from discord.ext.commands import MissingPermissions
import asyncio
from discord.interactions import Interaction
import keep_alive
import data
import re
#import pandas as pd  Espèce de gay BRUH ici on aime pas les pédales >:(
# from replit import db
import csv
import json
import requests
import io
from googletrans import Translator
from privateai_client import PAIClient
from privateai_client import request_objects

keep_alive.keep_alive()

prefix = "/"
client = discord.Client(intents=discord.Intents.all())
bot = commands.Bot(command_prefix=prefix,
                   description="Bot développé par 10RD et Lifzerr pour le fun",
                   intents=discord.Intents.all())

idLord = 583268098983985163
idLifzerr = 523926198930243584


# Infos du bot
@bot.event
async def on_ready():
  print("Connecté")
  try:
    synced = await bot.tree.sync()
    print(f"Synchronized {len(synced)} commands")
  except Exception as e:
    print(e)

  user = bot.get_user(idLord)

  if user:
    try:
      await user.send("Prêt")
      print("Message envoyé à l'hote")
    except discord.Forbidden:
      print(
          f"Impossible d'envoyer un message privé à l'utilisateur avec l'ID {idLord}"
      )

  await bot.change_presence(status=discord.Status.online,
                            activity=discord.Activity(
                                type=discord.ActivityType.playing,
                                name="Trie les gens tah 1942"))


"""
EVENTS 
"""


@bot.event
async def on_message(message):
  # Variables
  compteur = 0

  # Ne prend pas en compte les messages des bots
  if message.author.bot:
    return

  # Mention SEULE du bot (affiche les différentes fonctionnalités)
  if bot.user in message.mentions and len(
      message.mentions) == 1 and message.content.strip(
      ) == f'<@{bot.user.id}>':

    # Récupération des commandes et leur desc
    command_list = [
        f"{command.name}: {command.description}\n"
        for command in bot.tree.walk_commands()
    ]

    # Liste des commandes
    embed = discord.Embed(title="Liste des commandes :", color=0x00FFFF)
    sans_admin = [
        command for command in command_list if '[admin]' not in command
    ]
    commandes = '\n'.join(sans_admin)
    embed.add_field(name="A utiliser avec '/'", value=commandes, inline=False)

    await message.reply(
        f"{random.choice(data.salutations)} {message.author.display_name}\n{data.listeCommandes}\n",
        embed=embed)

  for j in range(0, len(data.salutations)):
    if data.salutations[j].lower() == message.content.lower():
      await message.reply(
          f"{random.choice(data.salutations)} {message.author.display_name} \n{random.choice(data.politesse)} ?"
      )

  # Répondre à "et toi" seulement si le bot est mentionné
  if bot.user.mentioned_in(message) and "et toi" in message.content.lower():
    await message.reply(
        "Je suis un bot.\nTant que ma connexion est bonne, je suis heureux (ce n'est pas le cas actuellement)."
    )

  # Vérification des mots racistes
  for i in range(0, len(data.listeMotRacistes)):
    if data.listeMotRacistes[i].lower() in message.content.lower():
      compteur = compteur + 1

  # Correction de la vérification du compteur et réponse associée
  if compteur != 0:
    if compteur >= 2:
      await message.reply(f"Tu es très raciste {message.author.display_name}")
    else:
      await message.reply(
          f"Je crois que tu es raciste {message.author.display_name}")

  # Vérification du banned content
  for i in data.arabe:
    if i in message.content.lower():
      await message.reply("Sale arabe, rentre chez toi :p")
      return

  # Menaces de ban
  for i in range(0, len(data.bannedContent)):
    if data.bannedContent[i].lower() in message.content.lower():
      gifToSend = random.choice(data.attention)
      embed = discord.Embed()
      embed.set_image(url=gifToSend)
      await message.reply(
          f"La prochaine fois c'est le ban {message.author.display_name}, tu es méchant"
      )
      await message.reply(embed=embed)
      return

  # Réponse à "quoi"
  # Virer la ponctuation
  quoi = message.content.lower().strip(".,!?")
  if re.search(r"quoi\s*([.,!?])?$", quoi):
    await message.reply(f'{random.choice(data.feur)}')

  # Réponse à "nice" / "noice"
  if 'nice' in message.content.lower() or 'noice' in message.content.lower():
    await message.reply(
        "https://media1.tenor.com/m/H6sjheSkU1wAAAAC/noice-nice.gif")

  # Reset du compteur
  compteur = 0


# Message de bienvenue
@bot.event
async def on_member_join(member):
  channel = member.guild.system_channel
  if channel:
    for i in range(0, len(data.nomArabes)):
      if data.nomArabes[i] in member.name.lower():
        embed = discord.Embed(
            title="Bienvenue",
            description=f"Retourne dans ton pays, sal arabe {member.mention}",
            color=discord.Color.red())
        await channel.send(embed=embed)
        return
    embed = discord.Embed(
        title="Bienvenue",
        description=f"Bienvenue à {member.mention} sur le serveur !",
        color=discord.Color.green())
    embed.set_image(url=random.choice(data.gifBienvenue))
    await channel.send(embed=embed)


"""
COMMANDES /
"""


#Commande de ping
@bot.tree.command(name="ping", description="Retour de la latence du bot")
async def ping(interaction: discord.Interaction):
  gif_url = random.choice(data.gifCringe)
  embed = discord.Embed()
  embed.set_image(url=gif_url)
  await interaction.response.send_message(
      f"Mon temps de traitement est de {bot.latency} secondes \n C'est un peu lent, je sais :confounded::point_right::point_left:",
      embed=embed)


#Commande de ping sans gif
@bot.tree.command(name="pings", description="Ping sans gif")
async def pings(interaction: discord.Interaction):
  await interaction.response.send_message(
      f"Temps de traitement : {bot.latency} s")


#Commande de ban
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
          "Mais t'es con ? Utilise la commande suicide pour faire ça!")
    else:
      if reason is None:
        reason = f"None provided by {interaction.user.name}"
      await member.ban(reason=reason)
      await interaction.response.send_message(
          f"{interaction.user.mention}, {member.mention} a bien été ban!\n\nRaison: {reason}"
      )
  except commands.MissingPermissions as e:
    await interaction.response.send_message(
        f"Tu n'as pas les permissions requises pour kick quelqu'un: {e}")
  except discord.Forbidden as e:
    await interaction.response.send_message(
        f"Je suis pauvre, je n'ai pas les permissions de faire ça : {e}")
  except Exception as e:
    await interaction.response.send_message(
        f"Oups... y'a une couille dans le potage : {e}")


# Commande de suicide
@bot.tree.command(
    name="suicide",
    description="Mdr tu te suicide (perma ban de toi même miskine)")
@commands.has_permissions(ban_members=True, administrator=True)
async def suicide(interaction, member: discord.Member):
  try:
    if member.id == member.id:
      await member.ban(reason=None)
      await interaction.response.send_message(
          f"{interaction.user}, s'est suicidé")
    else:
      await interaction.response.send_message(
          "Tu ne peux pas suicider quelqu'un d'autre !")
  except commands.MissingPermissions as e:
    await interaction.response.send_message(
        f"Tu n'as pas les permissions requises pour kick quelqu'un: {e}")
  except discord.Forbidden as e:
    await interaction.response.send_message(
        f"Je suis pauvre, je n'ai pas les permissions de faire ça : {e}")
  except Exception as e:
    await interaction.response.send_message(
        f"Oups... y'a une couille dans le potage : {e}")


# Commande de unban
@bot.tree.command(name="unban",
                  description="Son racisme était peut-être utile finalement")
async def unban(ctx,
                user: discord.User,
                reason: str = "Aucune raison spécifiée"):
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


#Commande de kick
@bot.tree.command(name="kick", description="Dégager un migrant")
async def kick(ctx, user: discord.User):
  await ctx.guild.kick(user)
  await ctx.send(f"{user} a été expulsé tah les migrants (ah non).")


# Commande de clear
@bot.tree.command(
    name="clear",
    description="Clear un nombre choisi de messages dans la conversation")
async def clear(ctx, amount: int):
  # On va éviter de planter les serveurs de replit, et ton Xiaomi poubelle <- tg
  if amount > 50:
    await ctx.send(f"Tu ne peux pas supprimer autant de messages")
  else:
    async for message in ctx.channel.history(limit=amount):
      await message.delete()
    return


#Commande de gifs
@bot.tree.command(name="gif", description="Envoyer un gif")
async def gif(interaction: discord.Interaction):
  gifToSend = random.choice(data.listeGifs)
  embed = discord.Embed()
  embed.set_image(url=gifToSend)
  await interaction.response.send_message(embed=embed)


# Commande de giflist
@bot.tree.command(name="giflist",
                  description="[admin] : Envoyer la liste des gifs")
async def giflist(interaction: discord.Interaction):
  """if interaction.user.id != data.listeDesAdmins.values():
    await interaction.channel.send(
        "Vous n'êtes pas autorisé à exécuter cette commande.")
    return"""
  for gif in data.listeGifs:
    embed = discord.Embed()
    embed.set_image(url=gif)
    await interaction.channel.send(embed=embed)
  await interaction.channel.send(
      f"Il y a {len(data.listeGifs)} gifs dans la liste")


#Fonction anti-crash pour le chatbot
async def reponsechat(payload, question, interaction: discord.Interaction):
  # Envoi de la requête à l'API de chatbot
  headers = {
      "Authorization":
      "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYmFkYjIzOTMtNzA2Yy00Mzg5LWJlZGEtYTIzYzY0NmNkODczIiwidHlwZSI6ImFwaV90b2tlbiJ9.eU_g2u6jGl9f_YCbrRndfOA1bdhJPY4vgxZBYct7WR4"
  }
  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjNhNjEyZTUtOTcwMy00OWU0LWJlNDktNDBmODQyZTE0NWFlIiwidHlwZSI6ImFwaV90b2tlbiJ9.jYzcAVG6UaBgQg61XnJVpr8OyYIbbUo3GmtqzKtD6jo
  url = "https://api.edenai.run/v2/text/chat"

  response = requests.post(url, json=payload, headers=headers)

  # Traitement de la réponse
  if response.status_code == 200:
    result = json.loads(response.text)
    generated_text = result['openai']['generated_text']
    await interaction.channel.send(f"\n{generated_text}")
  else:
    await interaction.channel.send(
        "\nUne erreur s'est produite lors de la communication avec le chatbot."
    )


#Commande de chatbot
@bot.tree.command(name="chat", description="Discutez avec le bot")
async def chat(interaction: discord.Interaction, *, question: str):
  # Préparation de la requête à l'API de chatbot

  payload = {
      "providers": "openai",
      "text": question,
      "chatbot_global_action": data.aiprompt,
      "previous_history": [],
      "temperature": 0.0,
      "max_tokens": 1500,
      "fallback_providers": ""
  }
  await interaction.response.send_message(f"{interaction.user} : {question}")
  reponse = reponsechat(payload, question, interaction)
  await reponse


#Commande de chatbot de droite
@bot.tree.command(
    name="chad",
    description="Discutez avec le bot de façon non politiquement correcte")
async def chad(interaction: discord.Interaction, *, question: str):
  # Préparation de la requête à l'API de chatbot

  payload = {
      "providers": "openai",
      "text": question,
      "chatbot_global_action": data.aipromptDroite,
      "previous_history": [],
      "temperature": 0.0,
      "max_tokens": 1500,
      "fallback_providers": ""
  }
  await interaction.response.send_message(f"{interaction.user} : {question}")
  await reponsechat(payload, question, interaction)


# Essaie nouvelle API
@bot.tree.command(name="chate", description="Discutez avec le bot")
async def chate(interaction: discord.Interaction, *, question: str):
  client = PAIClient(url="https://api.private-ai.com/deid",
                     api_key="9edf80d36eb846848dbdfa95a96bfcf9")
  text_request = request_objects.process_text_obj(text=['question'])
  response = client.process_text(text_request)

  await interaction.response.send_message(response.processed_text)


"""
client = PAIClient(url="https://api.private-ai.com/deid", api_key=9edf80d36eb846848dbdfa95a96bfcf9)
text_request = request_objects.process_text_obj(text=["My sample name is John Smith"])
response = client.process_text(text_request)

print(text_request.text)
print(response.processed_text)
"""


# Commande 8ball
@bot.tree.command(name="8ball",
                  description='Posez une question à la "boule magique"')
async def eight_ball(interaction: discord.Interaction, *, question: str):
  if question.endswith("?"):
    response = random.choice(data.r8ball)
    embed = discord.Embed(title="Boule Magique (Wallah c'est vrai)",
                          description=None,
                          color=0x9400D3)
    embed.add_field(name=f"Question de {interaction.user}",
                    value=question,
                    inline=False)
    embed.add_field(name="Réponse", value=response, inline=False)
    await interaction.response.send_message(embed=embed)
  else:
    await interaction.response.send_message(
        "Apprend à écrire :/\nGénéralement on met un point d'interrogation à la fin des questions.\nSi tu ne sais pas comment faire, voila un exemple :\n```Est tu débile ???????????```"
    )


# Commande pour générer une image à partir du texte
@bot.tree.command(
    name="image_generation",
    description=
    "Générer une image avec un texte donné (mais en anglais (mais c'est gratuit))"
)
async def image_generation(interaction: discord.Interaction, *, demande: str):
  # Envoyer un message pour indiquer que la demande est prise en compte
  await interaction.response.send_message(
      f'Demande prise en compte : {demande}')

  # Retirer les caractères spéciaux et remplacer les espaces par des '%20'
  texte_final = re.sub(r'[^\w\s]', '', demande)
  texte_final = texte_final.replace(' ', '%20')
  # Créer l'URL de l'image
  image_url = f"https://image.pollinations.ai/prompt/{texte_final}.png"
  # Créer l'embed avec l'URL de l'image
  embed = discord.Embed()
  embed.set_image(url=image_url)
  # Envoyer l'embed
  await interaction.channel.send(embed=embed)


@bot.tree.command(name="anime", description="Donne un lien vers un anime")
async def anime(interaction, nom_anime: str, plateforme: str):
  plateformes = {
      "voiranime": "https://v5.voiranime.com/anime/",
      "animesama": "https://anime-sama.fr/catalogue/"
  }
  plateforme = plateforme.lower()
  if plateforme not in plateformes:
    await interaction.response.send_message("Plateforme non prise en charge")
    return

  base_url = plateformes[plateforme]
  bon_mot = nom_anime.lower().replace(" ", "-")
  url_complet = f"{base_url}{bon_mot}/"

  try:
    response = requests.head(url_complet)
    if response.status_code >= 200 and response.status_code < 300:
      await interaction.response.send_message(
          f"Voici le lien vers {nom_anime} sur {plateforme.capitalize()}:\n {url_complet}"
      )
    else:
      await interaction.response.send_message(
          f"Animé {nom_anime} pas trouvé sur la plateforme {plateforme.capitalize()}"
      )
  except requests.exceptions.RequestException:
    await interaction.response.send_message(
        "Erreur lors de la requête, veuillez réessayer plus tard")


"""
# Commande liste emojis
@bot.tree.command(name="liste_emojis",description='Donne la liste des emojis')
async def liste_emojis(ctx):
    # Récupérer l'objet Guild du serveur
    guild = ctx.guild
    # Récupérer la liste des émoticônes du serveur
    emojis = guild.emojis
    # Afficher la liste des émoticônes
    await ctx.send(f"Voici la liste des émoticônes sur ce serveur :\n{emojis}")
"""


# Commande pour attribuer des rôles via des réactions
@bot.tree.command(name="roleattribution", description="Crée un message pour l'attribution automatique de rôles avec des réactions")
@app_commands.checks.has_permissions(administrator=True)
async def roleattribution(interaction: discord.Interaction, message: str, color: str, roles: str):
    roles_list = [role.strip() for role in roles.split()]
    guild = interaction.guild

    # Conversion de la couleur française en hexadécimal
    color_hex = data.color_dict.get(color.lower())
    if color_hex is None:
        await interaction.response.send_message("Couleur invalide. Utilisez une couleur en français, par exemple 'rouge', 'bleu', etc.", ephemeral=True)
        return
    embed_color = discord.Color(color_hex)

    # Vérification et récupération des rôles mentionnés
    valid_roles = []
    role_ids = [int(role_id.strip("<@&>")) for role_id in roles_list if role_id.strip("<@&>").isdigit()]
    for role_id in role_ids:
        role = discord.utils.get(guild.roles, id=role_id)
        if role:
            valid_roles.append(role)
        else:
            await interaction.response.send_message(f"Rôle mentionné non trouvé", ephemeral=True)
            return

    # Création de l'embed
    embed = discord.Embed(title="Attribution de rôles", description=message, color=embed_color)
    emoji_list = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤']  # Liste d'émojis prédéfinis (à étendre si nécessaire)

    if len(valid_roles) > len(emoji_list):
        await interaction.response.send_message("Trop de rôles pour les émojis disponibles", ephemeral=True)
        return

    emoji_role_dict = {}
    for i, role in enumerate(valid_roles):
        embed.add_field(name=f"Rôle {role.name}", value=f"Réagissez avec {emoji_list[i]}", inline=False)
        emoji_role_dict[emoji_list[i]] = role

    # Envoi de l'embed et ajout des réactions
    bot_message = await interaction.channel.send(embed=embed)
    for emoji in emoji_role_dict:
        await bot_message.add_reaction(emoji)

    # Sauvegarde de l'ID du message et des rôles associés (exemple basique, à améliorer pour une persistance)
    role_message_data[bot_message.id] = emoji_role_dict
    await interaction.response.send_message("Message de rôle créé avec succès", ephemeral=True)

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


TOKEN = "MTIwMDgxNTM3NTY4MDU0ODk1NQ.GAkwEL.7NMdEVmfdywYGzlj9BV7l_xWFtqfFHXvEEvgJE"
bot.run(TOKEN)
