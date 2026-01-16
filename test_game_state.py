#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to create a sample game_state.json
Use this to test if the viewer.html works properly
"""

import json
from datetime import datetime

# Sample game state with a few moves
state = {
    "current_game_url": "https://lichess.org/TEST123",
    "game_in_progress": True,
    "game_number": 1,
    "scores": {
        "claude": 0,
        "gpt": 0,
        "nulles": 0,
        "total": 0
    },
    "elapsed_time": "0h 2min",
    "last_move": "Claude: e2e4",
    "moves": "e2e4 e7e5 g1f3 b8c6 f1c4",
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# Save to game_state.json
with open('game_state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("✅ Test game_state.json created!")
print(f"📝 Contains {len(state['moves'].split())} moves: {state['moves']}")
print("\n🌐 Now open http://localhost:8000/viewer.html to test")
print("   (Make sure chess_battle.py is running for the web server)")
