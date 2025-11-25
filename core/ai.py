# core/ai.py

# On importe le client ASYNCHRONE
from openai import AsyncOpenAI
import confidentiel

# On importe les fonctions (on part du principe que history.py sera corrigé)
from .history import add_to_history, get_history, init_history

# On instancie le client ASYNCHRONE
client_ai = AsyncOpenAI(api_key=confidentiel.OPENAI_API_KEY)

# core/ai.py

# ... (imports et client_ai) ...

# La fonction doit être asynchrone
async def generate_reply(channel_id):
    # On récupère l'historique COMPLET
    full_history = get_history(channel_id)

    # 1. On extrait le System Prompt (le premier message)
    system_prompt = full_history[0]
    
    # 2. On prend les N derniers messages d'échange (excluant le system prompt)
    # On prend les 10 messages qui ont eu lieu après le system prompt initial.
    recent_messages = full_history[1:][-10:] 

    # 3. On reconstruit l'historique à envoyer à l'API
    # On commence toujours par le system prompt pour l'ancrer.
    msgs = [system_prompt] + recent_messages 

    # On ajoute la consigne générique à la fin (c'est une bonne pratique)
    msgs.append({
        "role": "system",
        "content": "Réponds toujours quelque chose, même si le message reçu est très court."
    })

    try:
# ... (le reste du code est inchangé) ...
        # On AWAIT l'appel
        res = await client_ai.chat.completions.create(
            model="gpt-4o-mini",      # Corrigé: gpt-4o-mini
            messages=msgs,
            max_tokens=2048,           # Corrigé: max_tokens
            temperature=0.7,
            frequency_penalty=0.2,
            presence_penalty=0.1,
        )
    except Exception as e:
        print("Erreur OpenAI :", e)
        rep = "ptdr le cerveau m'a lâché deux secondes"
        add_to_history(channel_id, "assistant", rep)
        return rep

    txt = res.choices[0].message.content or "ptdr j'ai bugué deux secondes"
    add_to_history(channel_id, "assistant", txt)
    return txt