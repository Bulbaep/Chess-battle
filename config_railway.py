import os

# Configuration pour Railway - lit les variables d'environnement
LICHESS_BOT_CLAUDE_TOKEN = os.environ.get('LICHESS_BOT_CLAUDE_TOKEN')
LICHESS_BOT_GPT_TOKEN = os.environ.get('LICHESS_BOT_GPT_TOKEN')
LICHESS_BOT_CLAUDE_USERNAME = os.environ.get('LICHESS_BOT_CLAUDE_USERNAME')
LICHESS_BOT_GPT_USERNAME = os.environ.get('LICHESS_BOT_GPT_USERNAME')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Game settings
TIME_CONTROL = "180+2"  # 3 minutes + 2 seconds increment
COLOR = "random"  # "white", "black", or "random"
GAME_DELAY = 15  # Seconds between games
