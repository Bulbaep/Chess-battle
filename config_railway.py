import os

# Configuration pour Railway - lit les variables d'environnement
# === LICHESS BOTS ===
LICHESS_BOT_CLAUDE_USERNAME = os.environ.get('LICHESS_BOT_CLAUDE_USERNAME')
LICHESS_BOT_CLAUDE_TOKEN = os.environ.get('LICHESS_BOT_CLAUDE_TOKEN')

LICHESS_BOT_GPT_USERNAME = os.environ.get('LICHESS_BOT_GPT_USERNAME')
LICHESS_BOT_GPT_TOKEN = os.environ.get('LICHESS_BOT_GPT_TOKEN')

# === API KEYS ===
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# === PARAMÈTRES DE JEU ===
# Temps de contrôle (Blitz: 3 minutes + 2 secondes par coup)
TIME_CONTROL = {
    "time": 3,  # Minutes
    "increment": 2  # Secondes par coup
}

# Modèles IA à utiliser
CLAUDE_MODEL = "claude-haiku-4-20250514"  # Haiku 4 - 4x moins cher que Sonnet
GPT_MODEL = "gpt-4o-mini"

# Nombre maximum de tentatives pour un coup invalide
MAX_RETRIES = 30
