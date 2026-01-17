#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Battle - Claude vs GPT Chess
================================
Script to automatically play Claude against ChatGPT on Lichess
"""

import berserk
import chess
import chess.pgn
from anthropic import Anthropic
from openai import OpenAI
import time
import sys
import threading
from datetime import datetime, timedelta
from config_railway import *
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

# === LOGGING SYSTEM ===
# Capture all print() output and save to logs.json

logs_list = []
logs_lock = threading.Lock()
original_print = print

def custom_print(*args, **kwargs):
    """Custom print that also saves to logs.json"""
    # Print to console normally
    original_print(*args, **kwargs)
    
    # Convert to string
    message = ' '.join(str(arg) for arg in args)
    
    # Add timestamp
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    
    # Add to logs list (thread-safe)
    with logs_lock:
        logs_list.append(log_entry)
        # Keep only last 500 logs
        if len(logs_list) > 500:
            logs_list.pop(0)
    
    # Save to file
    try:
        with open('logs.json', 'w') as f:
            json.dump({"logs": logs_list}, f)
    except:
        pass

# Replace built-in print
print = custom_print

# === INITIALIZATION ===
print("🎮 Initializing AI Battle...")

# Lichess clients
try:
    session_claude = berserk.TokenSession(LICHESS_BOT_CLAUDE_TOKEN)
    client_claude = berserk.Client(session_claude)
    
    session_gpt = berserk.TokenSession(LICHESS_BOT_GPT_TOKEN)
    client_gpt = berserk.Client(session_gpt)
    
    print("✅ Lichess connection successful")
except Exception as e:
    print(f"❌ Lichess connection error: {e}")
    sys.exit(1)

# AI clients
try:
    anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ AI APIs connection successful")
except Exception as e:
    print(f"❌ AI APIs connection error: {e}")
    sys.exit(1)

# Global variables for synchronization
current_game_id = None
game_ready = threading.Event()
challenge_accepted = threading.Event()
gpt_listener_running = True
game_in_progress = False
last_move_played = "-"
current_game_number = 0
current_moves_string = ""
claude_last_thought = "Waiting for game..."
gpt_last_thought = "Waiting for game..."

# === GAME STATE SAVE FUNCTION ===

def save_game_state(game_url=None, game_num=None, last_move=None, moves=None, claude_thought=None, gpt_thought=None):
    """Saves the current game state to a JSON file with AI thoughts"""
    global last_move_played, current_game_number, current_moves_string, claude_last_thought, gpt_last_thought
    
    if last_move:
        last_move_played = last_move
    if game_num:
        current_game_number = game_num
    if moves is not None:
        current_moves_string = moves
        print(f"📝 Updated current_moves_string: '{moves}' ({len(moves.split()) if moves else 0} moves)")
    if claude_thought:
        claude_last_thought = claude_thought
    if gpt_thought:
        gpt_last_thought = gpt_thought
    
    # Calculate elapsed time
    elapsed = datetime.now() - start_time
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    elapsed_str = f"{hours}h {minutes}min"
    
    # Calculate material score from current position if moves available
    material_white = 0
    material_black = 0
    threats_white = 0
    threats_black = 0
    
    if current_moves_string:
        try:
            temp_board = chess.Board()
            for move_uci in current_moves_string.split():
                temp_board.push_uci(move_uci)
            material_white, material_black = calculate_material_score(temp_board)
            # Count threats for each side
            threats_w, _ = analyze_threats(temp_board, 'white')
            threats_b, _ = analyze_threats(temp_board, 'black')
            threats_white = len(threats_w)
            threats_black = len(threats_b)
        except:
            pass
    
    state = {
        "current_game_url": game_url or "https://lichess.org",
        "game_in_progress": game_in_progress,
        "game_number": current_game_number,
        "scores": {
            "claude": scores["claude"],
            "gpt": scores["gpt"],
            "draws": scores["draws"],
            "total": scores["total"]
        },
        "elapsed_time": elapsed_str,
        "last_move": last_move_played,
        "moves": current_moves_string,
        "ai_thoughts": {
            "claude": {
                "thought": claude_last_thought,
                "material": material_white,
                "threats": threats_white
            },
            "gpt": {
                "thought": gpt_last_thought,
                "material": material_black,
                "threats": threats_black
            }
        },
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        with open('game_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"✅ game_state.json saved successfully")
    except Exception as e:
        print(f"⚠️  Error saving state: {e}")

# === CHALLENGE LISTENER FUNCTION (BOT GPT) ===

def gpt_challenge_listener():
    """Thread that listens for incoming challenges for GPT bot"""
    global current_game_id, gpt_listener_running, game_in_progress
    
    print("👂 GPT Bot listening for challenges...")
    
    while gpt_listener_running:
        try:
            for event in client_gpt.board.stream_incoming_events():
                if not gpt_listener_running:
                    break
                    
                if event['type'] == 'challenge':
                    challenge_data = event['challenge']
                    challenger = challenge_data['challenger']['name']
                    challenge_id = challenge_data['id']
                    
                    # Accepter seulement si pas de partie en cours et que c'est Claude
                    if challenger.lower() == LICHESS_BOT_CLAUDE_USERNAME.lower():
                        if not game_in_progress:
                            print(f"✅ Challenge received from {challenger}, accepting...")
                            try:
                                client_gpt.challenges.accept(challenge_id)
                                current_game_id = challenge_id
                                challenge_accepted.set()
                                print(f"✅ Challenge accepted : {challenge_id}")
                            except Exception as e:
                                print(f"❌ Error accepting challenge : {e}")
                        else:
                            print(f"⚠️  Challenge from {challenger} declined (game in progress)")
                            try:
                                client_gpt.challenges.decline(challenge_id)
                            except:
                                pass
                    else:
                        # Decline other challenges
                        try:
                            client_gpt.challenges.decline(challenge_id)
                        except:
                            pass
                            
                elif event['type'] == 'gameStart':
                    game_data = event['game']
                    game_id = game_data.get('gameId') or game_data.get('id')
                    if game_id:
                        current_game_id = game_id
                        game_ready.set()
                        
        except Exception as e:
            if gpt_listener_running:
                print(f"⚠️  Error in GPT listener : {e}")
                time.sleep(5)

# === SCORE COUNTER ===
scores = {
    "claude": 0,
    "gpt": 0,
    "draws": 0,
    "total": 0
}
start_time = datetime.now()

# === AI FUNCTIONS ===

def board_to_ascii(board):
    """Converts board to visual ASCII representation with Unicode symbols"""
    pieces_unicode = {
        'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
        'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    }
    
    result = "\n  a b c d e f g h\n"
    for i in range(8):
        rank = 8 - i
        result += f"{rank} "
        for j in range(8):
            square = chess.square(j, 7 - i)
            piece = board.piece_at(square)
            if piece:
                result += pieces_unicode.get(piece.symbol(), piece.symbol()) + " "
            else:
                result += ". "
        result += f"{rank}\n"
    result += "  a b c d e f g h\n"
    return result

def calculate_material_score(board):
    """Calculates material score for each color"""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    
    white_score = 0
    black_score = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_score += value
            else:
                black_score += value
    
    return white_score, black_score

def analyze_threats(board, color):
    """Analyzes threats and endangered pieces"""
    threats = []
    captures = []
    
    my_color = chess.WHITE if color == 'white' else chess.BLACK
    opponent_color = chess.BLACK if color == 'white' else chess.WHITE
    
    # Check attacked pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == my_color:
            # Is this piece attacked?
            if board.is_attacked_by(opponent_color, square):
                piece_name = chess.piece_name(piece.piece_type).upper()
                square_name = chess.square_name(square)
                threats.append(f"{piece_name} on {square_name}")
    
    # Search for possible captures
    for move in board.legal_moves:
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                piece_name = chess.piece_name(captured_piece.piece_type).upper()
                captures.append(f"{move.uci()} (capture {piece_name})")
    
    return threats, captures

def get_smart_moves(board):
    """Returns the most interesting moves (not all)"""
    legal_moves = list(board.legal_moves)
    
    # Prioritize: captures, checks, development
    captures = [m for m in legal_moves if board.is_capture(m)]
    checks = [m for m in legal_moves if board.gives_check(m)]
    
    # Development moves (knights, bishops)
    development = []
    for move in legal_moves:
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
            # If piece moves from its initial position
            if move.from_square in [chess.B1, chess.G1, chess.C1, chess.F1,  # White
                                     chess.B8, chess.G8, chess.C8, chess.F8]:  # Black
                development.append(move)
    
    # Combine: captures + checks + development + some others
    smart_moves = list(set(captures + checks + development))
    
    # If not enough, add random moves
    if len(smart_moves) < 10:
        remaining = [m for m in legal_moves if m not in smart_moves]
        smart_moves.extend(remaining[:10 - len(smart_moves)])
    
    return smart_moves[:15]  # Max 15 moves

def ask_claude_move(board_fen, color, invalid_moves=[]):
    """Ask Claude to play a move with full ASCII vision"""
    
    board_temp = chess.Board(board_fen)
    
    # Generate ASCII board
    ascii_board = board_to_ascii(board_temp)
    
    # Calculate material score
    white_score, black_score = calculate_material_score(board_temp)
    my_score = white_score if color == 'white' else black_score
    opp_score = black_score if color == 'white' else white_score
    diff = my_score - opp_score
    
    # Analyze threats
    threats, captures = analyze_threats(board_temp, color)
    
    # Smart recommended moves
    smart_moves = get_smart_moves(board_temp)
    smart_moves_str = ", ".join([m.uci() for m in smart_moves])
    
    # ALL LEGAL MOVES (complete list)
    all_legal_moves = list(board_temp.legal_moves)
    all_legal_moves_str = ", ".join([m.uci() for m in all_legal_moves])
    
    # History
    move_stack = list(board_temp.move_stack)
    last_moves = " ".join([m.uci() for m in move_stack[-4:]]) if len(move_stack) > 0 else "Game start"
    
    # Build prompt
    threats_str = "\n- ".join(threats) if threats else "No immediate threats"
    captures_str = "\n- ".join(captures[:5]) if captures else "No captures available"
    
    situation = "AHEAD" if diff > 0 else "BEHIND" if diff < 0 else "EQUAL"
    
    # Warning about invalid moves
    invalid_warning = ""
    if invalid_moves:
        invalid_warning = f"\n\n❌ WARNING! These moves are INVALID, do NOT play them again:\n{', '.join(invalid_moves)}\nChoose a DIFFERENT move!"
    
    prompt = f"""🎯 YOU ARE A CHESS GRANDMASTER - YOU PLAY {'WHITE (♙)' if color == 'white' else 'BLACK (♟)'}

CURRENT BOARD:
{ascii_board}

📊 MATERIAL SCORE:
White: {white_score} points | Black: {black_score} points
→ You are {situation} ({diff:+d} points)

⚠️ YOUR PIECES IN DANGER:
- {threats_str}

🎯 POSSIBLE CAPTURES:
- {captures_str}

📋 LAST MOVES: {last_moves}

🎲 RECOMMENDED MOVES:
{smart_moves_str}

⚔️ ALL LEGAL MOVES (you MUST choose from this list):
{all_legal_moves_str}{invalid_warning}

🏆 MISSION: WIN THE GAME!

STRATEGY (in order):
1. If CHECKMATE possible → Do it immediately!
2. If one of YOUR pieces is attacked → Save it or capture in exchange!
3. If you can CAPTURE opponent's material → Take it!
4. Otherwise → Develop pieces, control center, threaten

⛔ FORBIDDEN:
- Losing material for free
- Repeating the same move stupidly

📝 RESPONSE FORMAT (IMPORTANT):
Line 1: Brief thought (max 6 words, describe your plan IN ENGLISH)
Line 2: Your move in UCI format (ex: e2e4)

Example:
Protecting attacked knight
g1f3

Now play!"""

    try:
        message = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=80,  # Increased for thought + move
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text.strip()
        
        # Parse: line 1 = thought, line 2 = move
        lines = response_text.split('\n')
        if len(lines) >= 2:
            thought = lines[0].strip()
            move = lines[1].strip()
        else:
            # Fallback if format not respected
            thought = "Analyzing position"
            move = response_text.strip()
        
        print(f"💭 Claude thinks: '{thought}'")
        return move, thought
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return None, None

def ask_gpt_move(board_fen, color, invalid_moves=[]):
    """Ask GPT to play a move with full ASCII vision"""
    
    board_temp = chess.Board(board_fen)
    
    # Generate ASCII board
    ascii_board = board_to_ascii(board_temp)
    
    # Calculate material score
    white_score, black_score = calculate_material_score(board_temp)
    my_score = white_score if color == 'white' else black_score
    opp_score = black_score if color == 'white' else white_score
    diff = my_score - opp_score
    
    # Analyze threats
    threats, captures = analyze_threats(board_temp, color)
    
    # Smart recommended moves
    smart_moves = get_smart_moves(board_temp)
    smart_moves_str = ", ".join([m.uci() for m in smart_moves])
    
    # ALL LEGAL MOVES (complete list)
    all_legal_moves = list(board_temp.legal_moves)
    all_legal_moves_str = ", ".join([m.uci() for m in all_legal_moves])
    
    # History
    move_stack = list(board_temp.move_stack)
    last_moves = " ".join([m.uci() for m in move_stack[-4:]]) if len(move_stack) > 0 else "Game start"
    
    # Build prompt
    threats_str = "\n- ".join(threats) if threats else "No immediate threats"
    captures_str = "\n- ".join(captures[:5]) if captures else "No captures available"
    
    situation = "AHEAD" if diff > 0 else "BEHIND" if diff < 0 else "EQUAL"
    
    # Warning about invalid moves
    invalid_warning = ""
    if invalid_moves:
        invalid_warning = f"\n\n❌ WARNING! These moves are INVALID, do NOT play them again:\n{', '.join(invalid_moves)}\nChoose a DIFFERENT move!"
    
    prompt = f"""🎯 YOU ARE A CHESS GRANDMASTER - YOU PLAY {'WHITE (♙)' if color == 'white' else 'BLACK (♟)'}

CURRENT BOARD:
{ascii_board}

📊 MATERIAL SCORE:
White: {white_score} points | Black: {black_score} points
→ You are {situation} ({diff:+d} points)

⚠️ YOUR PIECES IN DANGER:
- {threats_str}

🎯 POSSIBLE CAPTURES:
- {captures_str}

📋 LAST MOVES: {last_moves}

🎲 RECOMMENDED MOVES:
{smart_moves_str}

⚔️ ALL LEGAL MOVES (you MUST choose from this list):
{all_legal_moves_str}{invalid_warning}

🏆 MISSION: WIN THE GAME!

STRATEGY (in order):
1. If CHECKMATE possible → Do it immediately!
2. If one of YOUR pieces is attacked → Save it or capture in exchange!
3. If you can CAPTURE opponent's material → Take it!
4. Otherwise → Develop pieces, control center, threaten

⛔ FORBIDDEN:
- Losing material for free
- Repeating the same move stupidly

📝 RESPONSE FORMAT (IMPORTANT):
Line 1: Brief thought (max 6 words, describe your plan IN ENGLISH)
Line 2: Your move in UCI format (ex: e2e4)

Example:
Developing pieces to center
e7e5

Now play!"""

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,  # Increased for thought + move
            temperature=1.0
        )
        response_text = response.choices[0].message.content.strip()
        
        # Parse: line 1 = thought, line 2 = move
        lines = response_text.split('\n')
        if len(lines) >= 2:
            thought = lines[0].strip()
            move = lines[1].strip()
        else:
            # Fallback if format not respected
            thought = "Analyzing position"
            move = response_text.strip()
        
        print(f"💭 GPT thinks: '{thought}'")
        return move, thought
    except Exception as e:
        print(f"❌ GPT API error: {e}")
        return None, None
        
        # Parse: line 1 = thought, line 2 = move
        lines = response_text.split('\n')
        if len(lines) >= 2:
            thought = lines[0].strip()
            move = lines[1].strip()
        else:
            # Fallback if format not respected
            thought = "Analyzing position"
            move = response_text.strip()
        
        print(f"💭 GPT thinks: '{thought}'")
        return move, thought
    except Exception as e:
        print(f"❌ GPT API error: {e}")
        return None, None

def validate_and_clean_move(move_str, board):
    """Validates and cleans the move proposed by the AI - handles both UCI and algebraic notation"""
    # Clean the response
    original_move = move_str
    move_str = move_str.strip()
    
    # Remove quotes, but preserve case for algebraic notation
    move_str = move_str.replace('"', '').replace("'", '').replace('\n', '').replace('\r', '')
    
    print(f"🔍 Debug - Original move: '{original_move}' → Cleaned: '{move_str}'")
    
    # Try parsing as Standard Algebraic Notation (SAN) first - e.g., "Kxf2", "Nf3", "e4"
    try:
        move = board.parse_san(move_str)
        if move in board.legal_moves:
            print(f"✅ Parsed as algebraic notation (SAN): '{move_str}' → UCI: '{move.uci()}'")
            return move
    except Exception as e:
        print(f"🔍 Debug - Not valid SAN: '{move_str}' ({e})")
    
    # Try parsing as UCI - e.g., "e2e4", "g1f3"
    move_str_lower = move_str.lower().strip()
    
    # Remove extra spaces
    move_str_lower = ''.join(c for c in move_str_lower if c.isalnum())
    
    # If too long, take first characters
    if len(move_str_lower) > 5:
        move_str_lower = move_str_lower[:5]
    
    print(f"🔍 Debug - Trying UCI: '{move_str_lower}'")
    
    # Try to parse as UCI
    try:
        move = chess.Move.from_uci(move_str_lower)
        if move in board.legal_moves:
            print(f"✅ Parsed as UCI: '{move_str_lower}'")
            return move
        else:
            print(f"🔍 Debug - Move '{move_str_lower}' is not legal in this position")
    except Exception as e:
        print(f"🔍 Debug - Cannot parse as UCI: '{move_str_lower}' ({e})")
    
    # Try to find a similar move
    for legal_move in board.legal_moves:
        if legal_move.uci().startswith(move_str_lower[:4]):
            print(f"🔍 Debug - Similar move found: {legal_move.uci()}")
            return legal_move
    
    print(f"❌ No valid move found for: '{original_move}'")
    return None

# === FONCTION PRINCIPALE DE JEU ===

def play_game(game_number):
    """Play a complete game"""
    global current_game_id, game_in_progress
    
    # IMPORTANT: Reset flag at start
    game_in_progress = False
    
    print(f"\n{'='*60}")
    print(f"🎮 GAME #{game_number}")
    print(f"{'='*60}")
    
    # Reset events
    challenge_accepted.clear()
    game_ready.clear()
    current_game_id = None
    
    # Create challenge
    try:
        print(f"📤 {LICHESS_BOT_CLAUDE_USERNAME} challenges {LICHESS_BOT_GPT_USERNAME}...")
        challenge = client_claude.challenges.create(
            LICHESS_BOT_GPT_USERNAME,
            rated=False,
            clock_limit=TIME_CONTROL["time"] * 60,
            clock_increment=TIME_CONTROL["increment"],
            color="white"
        )
        
        # Try different ways to get challenge ID
        challenge_id = None
        if isinstance(challenge, dict):
            # Method 1: {"challenge": {"id": "..."}}
            challenge_id = challenge.get("challenge", {}).get("id")
            # Method 2: {"id": "..."}
            if not challenge_id:
                challenge_id = challenge.get("id")
        elif isinstance(challenge, str):
            # Method 3: Direct ID as string
            challenge_id = challenge
        
        print(f"🔍 Debug - Challenge received: {challenge}")
        print(f"🔍 Debug - Challenge ID extracted: {challenge_id}")
        
        if not challenge_id:
            print("❌ Error: Cannot create challenge")
            game_in_progress = False
            return None
        
        print(f"✅ Challenge created: {challenge_id}")
        
        # Wait for GPT to accept (30 second timeout)
        print("⏳ Waiting for GPT to accept challenge...")
        if not challenge_accepted.wait(timeout=30):
            print("❌ Timeout: GPT didn't accept challenge")
            game_in_progress = False
            try:
                client_claude.challenges.cancel(challenge_id)
            except:
                pass
            return None
        
        print("✅ Challenge accepted by GPT")
        game_in_progress = True  # Now block new challenges
        
        # Wait for game to start
        print("⏳ Waiting for game to start...")
        if not game_ready.wait(timeout=15):
            print("❌ Timeout: Game didn't start")
            game_in_progress = False
            return None
        
        game_id = current_game_id
        if not game_id:
            print("❌ Error: Game ID unavailable")
            game_in_progress = False
            return None
        
        # Game URL
        game_url = f"https://lichess.org/{game_id}"
        print(f"✅ Game started!")
        print(f"📍 Game link: {game_url}")
        print(f"\n{'='*60}")
        
        # Save initial state
        save_game_state(game_url=game_url, game_num=game_number)
        
    except Exception as e:
        print(f"❌ Error creating challenge: {e}")
        game_in_progress = False
        return None
    
    # === PLAY THE GAME ===
    
    # Initialiser le plateau
    board = chess.Board()
    move_number = 1
    
    # Streaming de la partie
    try:
        print("🔍 Debug - Starting game stream...")
        for event in client_claude.bots.stream_game_state(game_id):
            print(f"🔍 Debug - Event received : type={event.get('type')}")
            
            if event['type'] == 'gameFull':
                print("🔍 Debug - gameFull event received")
                state = event.get('state', {})
                moves = state.get('moves', '')
                print(f"🔍 Debug - gameFull moves: '{moves}'")
                
                # Save moves to game state
                save_game_state(moves=moves)
                
                # Treat first state as gameState too
                status = state.get('status', 'started')
                
                # Apply moves to board
                board = chess.Board()
                if moves:
                    for move_uci in moves.split():
                        try:
                            board.push_uci(move_uci)
                        except:
                            pass
                
                print(f"🔍 Debug - gameFull - Board: FEN={board.fen()}")
                print(f"🔍 Debug - gameFull - {'White' if board.turn == chess.WHITE else 'Black'}'s turn")
                
                # If it's our turn (white = Claude), play immediately
                if board.turn == chess.WHITE and status == 'started':
                    print(f"\n♟️  Move {move_number} | Claude's turn (white)...")
                    
                    invalid_moves = []  # Store invalid moves
                    claude_thought = "Analyzing position"  # Default thought
                    for attempt in range(MAX_RETRIES):
                        result = ask_claude_move(board.fen(), 'white', invalid_moves)
                        
                        if result and result[0]:  # Check if we got a move
                            move_str, claude_thought = result
                            move = validate_and_clean_move(move_str, board)
                            
                            if move:
                                try:
                                    client_claude.bots.make_move(game_id, move.uci())
                                    print(f"✅ Claude plays: {move.uci()}")
                                    save_game_state(last_move=f"Claude: {move.uci()}", claude_thought=claude_thought)
                                    time.sleep(3)  # Pause to allow viewers to see the move
                                    break
                                except Exception as e:
                                    print(f"❌ Error sending move: {e}")
                                    time.sleep(1)
                            else:
                                print(f"⚠️  Invalid move (attempt {attempt+1}/{MAX_RETRIES}): {move_str}")
                                invalid_moves.append(move_str)  # Add to invalid list
                        
                        if attempt == MAX_RETRIES - 1:
                            print("❌ Claude couldn't play a valid move. Resigning.")
                            game_in_progress = False
                            try:
                                client_claude.bots.resign_game(game_id)
                            except:
                                pass
                            return 'gpt'
                        
                        time.sleep(1)
                
            elif event['type'] == 'gameState':
                print("🔍 Debug - gameState event received")
                moves = event.get('moves', '')
                status = event.get('status', '')
                winner = event.get('winner', '')
                print(f"🔍 Debug - gameState moves: '{moves}', status: '{status}'")
                
                # Save moves to game state
                print(f"💾 Saving {len(moves.split()) if moves else 0} moves to game_state.json")
                save_game_state(moves=moves)
                
                # Check if game is over
                if status == 'mate' or status == 'resign' or status == 'draw' or status == 'timeout' or status == 'outoftime':
                    print(f"\n{'='*60}")
                    print(f"🏁 Game over: {status}")
                    game_in_progress = False  # Allow new challenges
                    
                    if status == 'mate' or status == 'resign' or status == 'timeout' or status == 'outoftime':
                        if winner == 'white':
                            print("🏆 Claude victory (white)!")
                            return 'claude'
                        else:
                            print("🏆 GPT victory (black)!")
                            return 'gpt'
                    else:
                        print("⚖️  Draw !")
                        return 'draw'
                
                # Appliquer les coups au plateau
                board = chess.Board()
                if moves:
                    for move_uci in moves.split():
                        try:
                            board.push_uci(move_uci)
                        except:
                            pass
                
                print(f"🔍 Debug - Board after moves: FEN={board.fen()}")
                print(f"🔍 Debug - {'White' if board.turn == chess.WHITE else 'Black'}'s turn")
                print(f"🔍 Debug - board.turn == chess.WHITE ? {board.turn == chess.WHITE}")
                
                # Check if game is over by chess rules
                if board.is_game_over():
                    result = board.result()
                    print(f"\n{'='*60}")
                    print(f"🏁 Game over: {result}")
                    game_in_progress = False  # Allow new challenges
                    
                    if result == "1-0":
                        print("🏆 Claude victory (white)!")
                        return 'claude'
                    elif result == "0-1":
                        print("🏆 GPT victory (black)!")
                        return 'gpt'
                    else:
                        print("⚖️  Draw!")
                        return 'draw'
                
                # Whose turn is it?
                if board.turn == chess.WHITE:
                    # Claude's turn
                    print(f"\n♟️  Move {move_number} | Claude's turn (white)...")
                    
                    invalid_moves = []  # Store invalid moves
                    claude_thought = "Analyzing position"  # Default thought
                    for attempt in range(MAX_RETRIES):
                        # Pass invalid moves to function
                        result = ask_claude_move(board.fen(), 'white', invalid_moves)
                        
                        if result and result[0]:  # Check if we got a move
                            move_str, claude_thought = result
                            move = validate_and_clean_move(move_str, board)
                            
                            if move:
                                try:
                                    client_claude.bots.make_move(game_id, move.uci())
                                    print(f"✅ Claude plays: {move.uci()}")
                                    save_game_state(last_move=f"Claude: {move.uci()}", claude_thought=claude_thought)
                                    time.sleep(3)  # Pause to allow viewers to see the move
                                    break
                                except Exception as e:
                                    print(f"❌ Error sending move: {e}")
                                    time.sleep(1)
                            else:
                                print(f"⚠️  Invalid move (attempt {attempt+1}/{MAX_RETRIES}): {move_str}")
                                invalid_moves.append(move_str)  # Add to invalid list
                        
                        if attempt == MAX_RETRIES - 1:
                            print("❌ Claude couldn't play a valid move. Resigning.")
                            game_in_progress = False
                            try:
                                client_claude.bots.resign_game(game_id)
                            except:
                                pass
                            return 'gpt'
                        
                        time.sleep(1)
                    
                else:
                    # GPT's turn
                    print(f"♟️  Move {move_number} | GPT's turn (black)...")
                    
                    invalid_moves = []  # Store invalid moves
                    gpt_thought = "Analyzing position"  # Default thought
                    for attempt in range(MAX_RETRIES):
                        # Pass invalid moves to function
                        result = ask_gpt_move(board.fen(), 'black', invalid_moves)
                        
                        if result and result[0]:  # Check if we got a move
                            move_str, gpt_thought = result
                            move = validate_and_clean_move(move_str, board)
                            
                            if move:
                                try:
                                    client_gpt.bots.make_move(game_id, move.uci())
                                    print(f"✅ GPT plays: {move.uci()}")
                                    save_game_state(last_move=f"GPT: {move.uci()}", gpt_thought=gpt_thought)
                                    move_number += 1
                                    time.sleep(3)  # Pause to allow viewers to see the move
                                    break
                                except Exception as e:
                                    print(f"❌ Error sending move: {e}")
                                    time.sleep(1)
                            else:
                                print(f"⚠️  Invalid move (attempt {attempt+1}/{MAX_RETRIES}): {move_str}")
                                invalid_moves.append(move_str)  # Add to invalid list
                        
                        if attempt == MAX_RETRIES - 1:
                            print("❌ GPT couldn't play a valid move. Resigning.")
                            game_in_progress = False
                            try:
                                client_gpt.bots.resign_game(game_id)
                            except:
                                pass
                            return 'claude'
                        
                        time.sleep(1)
                
    except Exception as e:
        print(f"❌ Error during game: {e}")
        return None
    
    # Initialize board
    board = chess.Board()
    move_number = 1
    
    # Stream game
    try:
        for event in client_claude.bots.stream_game_state(game_id):
            
            if event['type'] == 'gameFull':
                state = event.get('state', {})
                moves = state.get('moves', '')
                
            elif event['type'] == 'gameState':
                moves = event.get('moves', '')
                status = event.get('status', '')
                winner = event.get('winner', '')
                
                # Check if game is over
                if status == 'mate' or status == 'resign' or status == 'draw' or status == 'timeout' or status == 'outoftime':
                    print(f"\n{'='*60}")
                    print(f"🏁 Game over: {status}")
                    game_in_progress = False  # Allow new challenges
                    
                    if status == 'mate' or status == 'resign' or status == 'timeout' or status == 'outoftime':
                        if winner == 'white':
                            print("🏆 Claude victory (white)!")
                            return 'claude'
                        else:
                            print("🏆 GPT victory (black)!")
                            return 'gpt'
                    else:
                        print("⚖️  Draw!")
                        return 'draw'
                
                # Apply moves to board
                board = chess.Board()
                if moves:
                    for move_uci in moves.split():
                        board.push_uci(move_uci)
                
                # Whose turn is it?
                if board.turn == chess.WHITE:
                    # Claude's turn
                    print(f"\n♟️  Move {move_number} | Claude's turn (white)...")
                    
                    claude_thought = "Analyzing position"  # Default thought
                    for attempt in range(MAX_RETRIES):
                        result = ask_claude_move(board.fen(), 'white')
                        
                        if result and result[0]:  # Check if we got a move
                            move_str, claude_thought = result
                            move = validate_and_clean_move(move_str, board)
                            
                            if move:
                                try:
                                    client_claude.bots.make_move(game_id, move.uci())
                                    print(f"✅ Claude plays: {move.uci()}")
                                    save_game_state(last_move=f"Claude: {move.uci()}", claude_thought=claude_thought)
                                    time.sleep(3)  # Pause to allow viewers to see the move
                                    break
                                except Exception as e:
                                    print(f"❌ Error sending move: {e}")
                            else:
                                print(f"⚠️  Invalid move (attempt {attempt+1}/{MAX_RETRIES}): {move_str}")
                        
                        if attempt == MAX_RETRIES - 1:
                            print("❌ Claude couldn't play a valid move. Resigning.")
                            client_claude.bots.resign_game(game_id)
                            return 'gpt'
                    
                else:
                    # GPT's turn
                    print(f"♟️  Move {move_number} | GPT's turn (black)...")
                    
                    gpt_thought = "Analyzing position"  # Default thought
                    for attempt in range(MAX_RETRIES):
                        result = ask_gpt_move(board.fen(), 'black')
                        
                        if result and result[0]:  # Check if we got a move
                            move_str, gpt_thought = result
                            move = validate_and_clean_move(move_str, board)
                            
                            if move:
                                try:
                                    client_gpt.bots.make_move(game_id, move.uci())
                                    print(f"✅ GPT plays: {move.uci()}")
                                    save_game_state(last_move=f"GPT: {move.uci()}", gpt_thought=gpt_thought)
                                    move_number += 1
                                    time.sleep(3)  # Pause to allow viewers to see the move
                                    break
                                except Exception as e:
                                    print(f"❌ Error sending move: {e}")
                            else:
                                print(f"⚠️  Invalid move (attempt {attempt+1}/{MAX_RETRIES}): {move_str}")
                        
                        if attempt == MAX_RETRIES - 1:
                            print("❌ GPT couldn't play a valid move. Resigning.")
                            game_in_progress = False
                            try:
                                client_gpt.bots.resign_game(game_id)
                            except:
                                pass
                            return 'claude'
                
    except Exception as e:
        print(f"❌ Error during game : {e}")
        game_in_progress = False
        return None

def display_scores():
    """Displays the score table"""
    elapsed = datetime.now() - start_time
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    
    print(f"\n{'='*60}")
    print(f"       🏆 AI BATTLE - GLOBAL SCORES 🏆")
    print(f"{'='*60}")
    print(f"🤖 Claude (White)  : {scores['claude']} wins")
    print(f"🤖 GPT    (Black)   : {scores['gpt']} wins")
    print(f"⚖️  Draws           : {scores['draws']} games")
    print(f"{'-'*60}")
    print(f"📊 Total games    : {scores['total']}")
    print(f"⏱️  Elapsed time     : {hours}h {minutes}min")
    print(f"{'='*60}\n")

# === HTTP SERVER FOR VIEWER ===

def start_http_server():
    """Starts an HTTP server to serve the HTML viewer"""
    try:
        # Change working directory to serve local files
        os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
        
        port = int(os.environ.get('PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"🌐 Web server started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️  HTTP server error: {e}")

# === MAIN LOOP ===

def main():
    """Main function - infinite game loop"""
    global gpt_listener_running
    
    print("\n🚀 Starting AI Battle!")
    print("⚠️  Press Ctrl+C to stop cleanly\n")
    
    # Initialize game_state.json with default state
    save_game_state()
    
    # Start HTTP server in separate thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    time.sleep(1)  # Let server start
    
    # Start listening thread for GPT bot
    gpt_thread = threading.Thread(target=gpt_challenge_listener, daemon=True)
    gpt_thread.start()
    
    # Wait for thread to start
    time.sleep(3)
    
    game_number = 1
    
    try:
        while True:
            result = play_game(game_number)
            
            if result:
                scores['total'] += 1
                
                if result == 'claude':
                    scores['claude'] += 1
                elif result == 'gpt':
                    scores['gpt'] += 1
                elif result == 'draw':
                    scores['draws'] += 1
                
                display_scores()
                save_game_state()  # Save state after each game
                
                # Pause between games (longer to avoid conflicts)
                print("⏳ 30 second pause before next game...\n")
                time.sleep(30)
                
                game_number += 1
            else:
                print("⚠️  Game cancelled. Retrying in 15 seconds...")
                time.sleep(15)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        gpt_listener_running = False
        display_scores()
        print("👋 Thanks for using AI Battle!\n")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        gpt_listener_running = False
        display_scores()
        sys.exit(1)

if __name__ == "__main__":
    main()
