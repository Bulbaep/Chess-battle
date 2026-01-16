# 🔍 Debugging Guide - AI Chess Battle Viewer

## Problem: Board doesn't update / No moves displayed

### Step 1: Check if game_state.json exists

**Windows:**
```bash
dir game_state.json
```

**Check contents:**
```bash
type game_state.json
```

The file should contain a "moves" field like:
```json
{
  "moves": "e2e4 e7e5 g1f3",
  ...
}
```

### Step 2: Test with sample data

Run the test script to create a sample game_state.json:
```bash
python test_game_state.py
```

Then open the viewer and check if the board shows the test position.

### Step 3: Check browser console

1. Open viewer: `http://localhost:8000/viewer.html`
2. Press **F12** (or right-click → Inspect)
3. Go to **Console** tab
4. Look for these messages:

**Good signs (everything working):**
```
📥 Loaded game state: {...}
📝 Moves string: e2e4 e7e5
♟️  Updating board with moves: e2e4 e7e5
✨ Updating board with new moves!
📋 Applying 2 moves: ['e2e4', 'e7e5']
✅ Applied move 1: e2e4
✅ Applied move 2: e7e5
✅ Board update complete!
```

**Problem indicators:**
```
⚠️  No moves field in game state!
❌ Invalid move: xyz123
⏳ Waiting for first game_state.json file...
```

### Step 4: Check Python terminal

When chess_battle.py is running, you should see:
```
💾 Saving 2 moves to game_state.json
📝 Updated current_moves_string: 'e2e4 e7e5' (2 moves)
✅ game_state.json saved successfully
```

**If you DON'T see these messages:**
- The moves aren't being saved
- Check if you're using the latest chess_battle.py

### Step 5: Manual test

Create a simple game_state.json manually:

```json
{
  "current_game_url": "https://lichess.org/TEST",
  "game_in_progress": true,
  "game_number": 1,
  "scores": {
    "claude": 0,
    "gpt": 0,
    "nulles": 0,
    "total": 0
  },
  "elapsed_time": "0h 1min",
  "last_move": "Test",
  "moves": "e2e4 e7e5",
  "last_update": "2026-01-15 14:30:25"
}
```

Save this as `game_state.json` in the same folder as viewer.html, then refresh the page.

**Expected result:** Board should show position after e2-e4 e7-e5 (King's Pawn opening)

### Step 6: Common issues and fixes

**Issue:** "moves" field is empty string ""
- **Fix:** Wait for the first move to be played

**Issue:** Console shows "Invalid move: xyz"
- **Fix:** The move format from Lichess is wrong (rare, but possible)
- Check the terminal output to see actual moves

**Issue:** game_state.json not updating
- **Fix:** Restart chess_battle.py
- Make sure you're using the NEW version with debug messages

**Issue:** Board shows starting position but moves exist
- **Fix:** Check browser console for JavaScript errors
- Try refreshing the page (Ctrl+F5)
- Clear browser cache

### Step 7: Verify files

Make sure you have the LATEST versions of:
- ✅ chess_battle.py (with debug messages "💾 Saving moves")
- ✅ viewer.html (with console.log debug)

### Quick Debug Checklist

```
□ chess_battle.py is running
□ Web server shows: "🌐 Web server started on http://localhost:8000"
□ game_state.json file exists
□ game_state.json contains "moves" field
□ Browser console (F12) shows no errors
□ Terminal shows "💾 Saving moves" messages
□ Refreshed viewer page (Ctrl+F5)
```

## Still not working?

Share these details:
1. Contents of game_state.json
2. Browser console output (F12 → Console tab)
3. Python terminal output (last 20 lines)
4. Screenshot of the viewer

This will help diagnose the exact issue! 🔍
