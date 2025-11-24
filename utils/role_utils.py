from cachetools import TTLCache

# ==========
# STOCKAGE
# ==========

# stocke les messages qui gèrent des rôles :
# { message_id : { emoji : role_id } }
role_message_data = {}

# cache des rôles pour éviter de spam l’API Discord
role_cache = TTLCache(maxsize=100, ttl=3600)


# ==========
#  FONCTIONS
# ==========

def register_role_message(message_id: int, mapping: dict):
    """
    mapping = { "🔴": role.id, "🟢": role.id }
    """
    role_message_data[message_id] = mapping


def get_role_mapping(message_id: int):
    return role_message_data.get(message_id, {})


def fetch_role(guild, role_id: int):
    return guild.get_role(role_id)


def get_role_cached(guild, role_id: int):
    role = role_cache.get(role_id)
    if role:
        return role

    role = fetch_role(guild, role_id)
    if role:
        role_cache[role_id] = role
    return role
