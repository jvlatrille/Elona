import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Chemins vers les prompts
PROMPTS_DIR = os.path.join(ROOT_DIR, "data", "prompts")

with open(os.path.join(PROMPTS_DIR, "prompt_general.txt"), "r", encoding="utf-8") as f:
    PROMPT_GENERAL = f.read()

with open(os.path.join(PROMPTS_DIR, "prompt_elona.txt"), "r", encoding="utf-8") as f:
    PROMPT_ELONA = f.read()
