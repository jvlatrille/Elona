# utils/anime_utils.py

import aiohttp # Remplacer requests par aiohttp
import asyncio

ANI_URL = "https://graphql.anilist.co"

QUERY = """
query ($name: String) {
    Media (search: $name, type: ANIME) {
        id
        title { romaji }
        coverImage { large }
    }
}
"""

# La fonction doit être ASYNCHRONE pour ne pas bloquer le bot
async def search_anime(name: str):
    """Cherche un anime par nom sur AniList."""
    try:
        # On utilise une session aiohttp
        async with aiohttp.ClientSession() as session:
            # On utilise un timeout
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with session.post(
                ANI_URL,
                json={"query": QUERY, "variables": {"name": name}},
                timeout=timeout
            ) as response:
                
                # Vérifier si la requête a réussi
                if response.status != 200:
                    print(f"Erreur API AniList: {response.status}")
                    return None
                
                data = await response.json()

        media = data.get("data", {}).get("Media")
        if not media:
            return None

        return {
            "name": media["title"]["romaji"],
            "cover": media["coverImage"]["large"]
        }
    
    # Gérer les erreurs de connexion ou de timeout
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Erreur lors de la requête AniList : {e}")
        return None
    except Exception as e:
        print(f"Erreur inattendue dans search_anime : {e}")
        return None