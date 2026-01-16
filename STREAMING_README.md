# 🎮 AI Battle Streaming System

## 📁 Updated Files

1. **chess_battle.py** - Main script with integrated streaming
2. **viewer.html** - Web visualization interface with **embedded chessboard**
3. **game_state.json** - Data file (created automatically)

## 🚀 How to Use

### Step 1: Place the Files
Put **chess_battle.py** and **viewer.html** in the same folder as your project (with config.py).

### Step 2: Launch the Script
```bash
python chess_battle.py
```

The script will automatically:
- ✅ Start web server on http://localhost:8000
- ✅ Create game_state.json file
- ✅ Launch Claude vs GPT games

### Step 3: Open the Viewer
Open your browser and go to:
```
http://localhost:8000/viewer.html
```

## 🎨 What You'll See

### Streaming Interface
- 🎬 **Live Interactive Chessboard** - Built-in chessboard with real-time updates (NO iframe!)
- ⚡ **Game Progress Tracker** - Current move number and whose turn it is
- 🔍 **Position Analysis** - Check detection, checkmate announcements
- 🏆 **Score Table** - Claude, GPT, draws, total
- ℹ️ **Real-time Information**:
  - Game status (in progress / waiting)
  - Current game number
  - Elapsed time since start
  - Last move played

### Automatic Updates
- Interface refreshes every **2 seconds**
- Board updates automatically with each move
- No need to manually reload the page
- Scores and links update automatically

## 🔧 Automatically Created Files

### game_state.json
This file is automatically created and updated by the script:
```json
{
  "current_game_url": "https://lichess.org/abc123",
  "game_in_progress": true,
  "game_number": 5,
  "scores": {
    "claude": 3,
    "gpt": 1,
    "nulles": 1,
    "total": 5
  },
  "elapsed_time": "0h 45min",
  "last_move": "Claude: e2e4",
  "moves": "e2e4 e7e5 g1f3 b8c6",
  "last_update": "2026-01-15 14:30:25"
}
```

## 🎯 Features

### In chess_battle.py
- ✅ Integrated HTTP server (port 8000)
- ✅ Automatic saving of each game's URL
- ✅ Tracking of last move played
- ✅ **Saves complete move sequence in UCI format**
- ✅ Score updates after each game
- ✅ Compatible with existing code (no regression)

### In viewer.html
- ✅ **Custom embedded chessboard (chessboard.js)**
- ✅ Modern and responsive design
- ✅ Live indicator animations
- ✅ Distinct colors for Claude/GPT/Draws
- ✅ Works on mobile and desktop
- ✅ No need to manually reload
- ✅ **No iframe issues - 100% self-contained**
- ✅ Automatic move detection and board update
- ✅ Check and checkmate announcements
- ✅ Turn indicator (Claude's turn / GPT's turn)

## 🔥 Why This Solution is Better

### Previous Problem (iframe)
- ❌ Lichess blocks embedding with X-Frame-Options
- ❌ Even /embed/ URLs can have restrictions
- ❌ Dependent on external service

### New Solution (custom board)
- ✅ **100% self-contained** - No external dependencies for display
- ✅ **No iframe issues** - Direct HTML/JS rendering
- ✅ **Real-time updates** - Board syncs with game_state.json
- ✅ **Professional look** - Uses chessboard.js (industry standard)
- ✅ **Automatic move playback** - Reads moves from Lichess API
- ✅ **Fully autonomous** - Perfect for 24/7 streaming

### Libraries Used
- **chessboard.js** - Beautiful chessboard rendering
- **chess.js** - Chess rules and move validation
- **jQuery** - DOM manipulation (required by chessboard.js)

All libraries are loaded from CDN - no installation needed!

## 📱 Sharing

### Share on Local Network
If you want others on your local network to see the stream:

1. Find your local IP:
   ```bash
   ipconfig
   ```
   (Look for IPv4 address, e.g. 192.168.1.100)

2. Modify chess_battle.py line 886:
   ```python
   server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
   ```

3. Others can access via:
   ```
   http://YOUR_IP:8000/viewer.html
   ```

## 🐛 Troubleshooting

### Board doesn't update with moves

**1. Check if game_state.json exists and contains moves:**
```bash
type game_state.json
```

Should show:
```json
{
  "moves": "e2e4 e7e5 g1f3",
  ...
}
```

**2. Test with sample data:**
```bash
python test_game_state.py
```
Then refresh viewer - board should show test position.

**3. Check browser console (F12):**
- Look for: `📥 Loaded game state:`
- Look for: `♟️ Updating board with moves:`
- Check for errors (red text)

**4. Check Python terminal:**
Should see:
```
💾 Saving 2 moves to game_state.json
📝 Updated current_moves_string: 'e2e4 e7e5' (2 moves)
✅ game_state.json saved successfully
```

**5. If still not working:**
- Restart chess_battle.py
- Clear browser cache (Ctrl+F5)
- Check DEBUG_GUIDE.md for detailed troubleshooting

### Viewer won't load
- Verify chess_battle.py is running
- Check no other program is using port 8000
- Try accessing http://localhost:8000 to test

### Viewer shows "Waiting"
- This is normal between games (30s pause)
- game_state.json will be created on first game

### Board doesn't update
- Check that game_state.json is being created
- Verify the "moves" field in game_state.json has content
- Open browser console (F12) to check for errors

### Pieces look weird
- CDN might be slow - refresh the page
- Check your internet connection

## 🎉 Technical Details

### How It Works
1. **Lichess API** → chess_battle.py reads moves in UCI format (e.g., "e2e4")
2. **JSON Storage** → Moves saved to game_state.json
3. **JavaScript Polling** → viewer.html checks JSON every 2 seconds
4. **Board Update** → chess.js validates moves, chessboard.js renders position

### Move Format
- Moves are saved in UCI (Universal Chess Interface) format
- Example: `"e2e4 e7e5 g1f3 b8c6"` = 4 moves (2 by each player)
- The JavaScript automatically:
  - Splits the string by spaces
  - Applies each move sequentially
  - Updates the visual board

## ⚡ Performance

- HTTP server is lightweight (Python SimpleHTTPRequestHandler)
- JSON file is small (~300 bytes)
- No impact on bot performance
- Refresh every 2s (no overload)
- Chessboard rendering is optimized (no lag)

Happy streaming! 🎮🏆

