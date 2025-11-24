# events/on_ready.py
import discord
import confidentiel

# La fonction DOIT être asynchrone pour load_extension
async def setup(bot):

    @bot.event
    async def on_ready():
        print("Bot connecté")

        # La synchronisation a été déplacée dans setup_hook (core/bot.py)

        # message au propriétaire
        if hasattr(confidentiel, "OWNER_ID"):
            try:
                user = await bot.fetch_user(confidentiel.OWNER_ID) # fetch_user est plus fiable
                if user:
                    await user.send("Bot lancé et commandes synchronisées !")
            except Exception as e:
                print(f"Impossible d'envoyer le DM au propriétaire : {e}")