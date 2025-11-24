# events/on_interaction.py

# Doit être asynchrone pour être chargé
async def setup(bot):
    
    @bot.event
    async def on_interaction(inter):
        # Tu peux mettre ta logique ici
        pass