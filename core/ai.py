# core/ai.py

# On importe le client ASYNCHRONE
from openai import AsyncOpenAI
import confidentiel

# On importe les fonctions (on part du principe que history.py sera corrigé)
from .history import add_to_history, get_history, init_history

# On instancie le client ASYNCHRONE
client_ai = AsyncOpenAI(api_key=confidentiel.OPENAI_API_KEY)

# La fonction doit être asynchrone
async def generate_reply(channel_id):
    # On suppose que get_history est valide (on le corrigera après)
    msgs = get_history(channel_id)[-10:]

    msgs.append({
        "role": "system",
        "content": "Réponds toujours quelque chose, même si le message reçu est très court."
    })

    try:
        # On AWAIT l'appel
        res = await client_ai.chat.completions.create(
            model="gpt-4o-mini",      # Corrigé: gpt-4o-mini
            messages=msgs,
            max_tokens=200,           # Corrigé: max_tokens
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