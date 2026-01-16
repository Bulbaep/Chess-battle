# ============================================
# AI CHESS BATTLE - Configuration Template
# ============================================
# 
# Rename this file to: config.py
# Then fill in your own credentials below
#

# === LICHESS BOT TOKENS ===
# Create your bots on https://lichess.org/@/your-username/bots
# Then generate API tokens for each bot

LICHESS_BOT_CLAUDE_TOKEN = "lip_YOUR_CLAUDE_BOT_TOKEN_HERE"
LICHESS_BOT_GPT_TOKEN = "lip_YOUR_GPT_BOT_TOKEN_HERE"

LICHESS_BOT_CLAUDE_USERNAME = "YourClaudeBotName"
LICHESS_BOT_GPT_USERNAME = "YourGPTBotName"


# === AI API KEYS ===
# Anthropic API: https://console.anthropic.com/
# OpenAI API: https://platform.openai.com/

ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_ANTHROPIC_KEY_HERE"
OPENAI_API_KEY = "sk-proj-YOUR_OPENAI_KEY_HERE"


# === AI MODELS ===
CLAUDE_MODEL = "claude-sonnet-4-20250514"
GPT_MODEL = "gpt-4o-mini"


# === GAME SETTINGS ===
# Time control format: "initial_time+increment" (in seconds)
# Examples:
#   "180+2"  = 3 minutes + 2 seconds per move (Blitz)
#   "600+5"  = 10 minutes + 5 seconds per move (Rapid)
#   "300+0"  = 5 minutes, no increment (Blitz)

TIME_CONTROL = "180+2"


# === RETRY SETTINGS ===
# Maximum number of attempts to play a valid move
# Increased to 5 to give AIs more chances to find a valid move
MAX_RETRIES = 5
