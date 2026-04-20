# Chess Game Specification

## 1. Project Overview

### 1.1 Project Name

**Chess Manager** - A fully-featured 2-player chess game built with Pygame

### 1.2 Project Type

Desktop chess game application

### 1.3 Core Feature Summary

A turn-based chess game featuring a complete move validation engine for all piece types, game timer tracking, captured pieces display, and standard win/draw condition detection.

### 1.4 Target Users

Chess enthusiasts who want to play local 2-player chess on desktop

---

## 2. Technical Architecture

### 2.1 Technology Stack

| Component | Technology |
|-----------|-------------|
| Game Engine | Pygame 2.x |
| Language | Python 3.8+ |
| Rendering | Pygame Surface (blitting) |
| Fonts | System fonts (fallback to default) |

### 2.2 Project Structure

```
chess_game/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── game.py              # Main game loop
│   ├── board.py             # Board representation
│   ├── piece.py             # Piece classes
│   ├── move_validator.py    # Move validation logic
│   ├── ui.py                # UI rendering
│   └── constants.py         # Game constants
└── assets/
    └── (optional piece sprites)
```

---

## 3. Visual Design Specification

### 3.1 Window Configuration

| Setting | Value |
|---------|-------|
| Window Size | 1200 x 800 pixels |
| Minimum Size | 1000 x 700 pixels |
| Window Title | "Chess Manager" |
| Resizable | Yes |
| Frame | Standard OS window frame |

### 3.2 Color Palette

| Element | Color | Hex Code |
|---------|-------|---------|
| Light Square | Cream | #F0D9B5 |
| Dark Square | Brown | #B58863 |
| Board Border | Dark Brown | #5C4033 |
| Background | Charcoal | #2D2D2D |
| UI Panel Background | Slate Gray | #3C3C3C |
| UI Panel Border | Dark Gray | #4A4A4A |
| Text Primary | Off-White | #E8E8E8 |
| Text Secondary | Light Gray | #A0A0A0 |
| Accent (White Turn) | Warm White | #FFFEF0 |
| Accent (Black Turn) | Warm Black | #1A1A1A |
| Highlight (Selected) | Gold | #FFD700 |
| Highlight (Valid Move) | Green (50% alpha) | #00FF00 |
| Highlight (Last Move) | Yellow (40% alpha) | #FFFF00 |
| Check Indicator | Red | #FF4444 |
| Button Background | Steel Blue | #4A6A8A |
| Button Hover | Light Steel Blue | #5A7A9A |

### 3.3 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Window Title | System Default | 18 | Bold |
| Turn Indicator | System Default | 16 | Bold |
| Game Status | System Default | 14 | Normal |
| Game Timer | Monospace | 20 | Bold |
| Captured Piece Label | System Default | 12 | Bold |
| Button Text | System Default | 14 | Bold |

### 3.4 Layout Specification

```
+------------------------------------------------------------------+
|  [Window Title: "Chess Manager"]                                   |
+------------------------------------------------------------------+
|                                                                  |
|  +------------------------+  +----------------------------------+  |
|  |                        |  |  WHITE                           |  |
|  |                        |  |  Timer: 00:05:32                 |  |
|  |    CHESS BOARD         |  |  Captured: ♕ ♖ ♗ ♘ ♙           |  |
|  |    (8x8 Grid)          |  +----------------------------------+  |
|  |    560x560 px          |  |                                  |  |
|  |                        |  |  Status: WHITE's Turn            |  |
|  |    a b c d e f g h     |  |  [New Game]  [Reset]             |  |
|  |    1 2 3 4 5 6 7 8     |  |                                  |  |
|  |                        |  +----------------------------------+  |
|  |                        |  |  BLACK                           |  |
|  |                        |  |  Timer: 00:05:32                 |  |
|  |                        |  |  Captured: ♛ ♜ ♝ ♞ ♟           |  |
|  +------------------------+  +----------------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

### 3.5 Board Dimensions

| Element | Dimension |
|---------|-----------|
| Board Area (with border) | 580 x 580 pixels |
| Inner Board Grid | 560 x 560 pixels |
| Square Size | 70 x 70 pixels |
| Coordinate Labels | 16 pixels font, 20 pixels margin |
| Border Width | 10 pixels |

### 3.6 UI Panel Layout

| Panel | Position | Size |
|-------|----------|------|
| Main UI Panel | Right side | 300 px width |
| Player Info (White) | Top-right | Full width, 180 px height |
| Game Status Panel | Middle-right | Full width, 120 px height |
| Player Info (Black) | Bottom-right | Full width, 180 px height |

### 3.7 Piece Rendering

#### Option 1: Unicode Chess Symbols (Primary)

| Piece | White Symbol | Black Symbol | Font Size |
|-------|--------------|---------------|-----------|
| King | ♔ | ♚ | 50 pt |
| Queen | ♕ | ♛ | 50 pt |
| Rook | ♖ | ♜ | 50 pt |
| Bishop | ♗ | ♝ | 50 pt |
| Knight | ♘ | ♞ | 50 pt |
| Pawn | ♙ | ♟ | 50 pt |

**Rendering Settings:**
- Center-aligned on each square
- White pieces: #FFFFFF with #333333 1px outline
- Black pieces: #1A1A1A with #CCCCCC 1px outline

#### Option 2: Visual Enhancement (Highlighted)

```
Selected Piece:
- Gold (#FFD700) 3px outline on square border

Valid Move Markers:
- Green circle (#00AA00) at square center, 20% opacity
- Circle radius: 15 pixels

Capture Moves:
- Red ring (#FF4444) at square center, 3px stroke
- Ring radius: 25 pixels

Last Move Highlight:
- From: Yellow (#FFFF00) tint, 30% opacity overlay
- To: Yellow (#FFFF00) tint, 30% opacity overlay

King In Check:
- Red glow effect on king's square (pulsing)
- Red (#FF0000) square border, 4px
```

---

## 4. Game Logic Specification

### 4.1 Board Representation

**Coordinate System:**
- Columns: a-h (x: 0-7)
- Rows: 1-8 (y: 7-0, white's perspective bottom)
- Internal: (x, y) where x=column, y=row

**Piece Storage:**
- 8x8 2D array storing Piece objects or None
- White pieces: Piece objects with color=WHITE
- Black pieces: Piece objects with color=BLACK

### 4.2 Piece Movement Rules

#### King (♔/♚)

```
Symbol: K
Valid Moves:
  - 1 square in any direction (8 directions)
  - Cannot move into check
Special Moves:
  - Castling:
    * Kingside: King moves 2 right, Rook jumps to King's left
    * Requirements:
      - King and Rook have not moved
      - No pieces between King and Rook
      - King not in check, not moving through check
    * Notation: O-O (kingside), O-O-O (queenside)
Color: Both (white ♔, black ♚)
Value: ∞ (incalculable)
```

#### Queen (♕/♛)

```
Symbol: Q
Valid Moves:
  - Any distance in any straight direction (4 directions)
  - Cannot jump over pieces
  - Captures by moving to opponent's square
Color: Both
Value: 9
```

#### Rook (♖/♜)

```
Symbol: R
Valid Moves:
  - Any distance horizontally or vertically (4 directions)
  - Cannot jump over pieces
  - Captures by moving to opponent's square
Color: Both
Value: 5
```

#### Bishop (♗/♝)

```
Symbol: B
Valid Moves:
  - Any distance diagonally (4 directions)
  - Cannot jump over pieces
  - Captures by moving to opponent's square
Color: Both
Value: 3
```

#### Knight (♘/♞)

```
Symbol: N
Valid Moves:
  - L-shape: 2 squares in one direction + 1 square perpendicular
  - 8 possible moves in L-pattern
  - Can jump over all pieces
  - Captures by landing on opponent's square
Color: Both
Value: 3
```

#### Pawn (♙/♟)

```
Symbol: P
Valid Moves:
  - Forward 1 square (toward opponent's side)
  - Forward 2 squares (only from starting position)
  - Cannot move forward if blocked
  - Cannot capture forward (only diagonally)
Special Moves:
  - Capture: Diagonally forward 1 square (enemy piece required)
  - En Passant:
    * Capture opponent's pawn that just moved 2 squares
    * Must be executed immediately
    * Pawn captures as if it moved behind opponent's pawn
  - Promotion:
    * When reaching opposite end of board
    * Automatically promotes to Queen
    * (Can be extended to allow choice: Q/R/B/N)
Color: Both (white ♙ moves up, black ♟ moves down)
Value: 1
Starting Position:
  - White: Row 1 (y=1), columns a-h
  - Black: Row 6 (y=6), columns a-h
```

### 4.3 Move Validation Process

```
1. Input: Source square, target square
2. Validate:
   a. Source square contains current player's piece
   b. Target square is different from source
   c. Basic move pattern is valid for piece type
   d. No friendly piece on target square
   e. Path is clear (for sliding pieces)
   f. Move doesn't leave own king in check
3. Output: Valid/Invalid with reason
```

### 4.4 Check Detection

```
Algorithm:
1. Find current player's King position
2. For each enemy piece:
   a. Generate all its legal moves
   b. If any move captures King → Check
3. Return check status
```

### 4.5 Turn Management

```
Turn Sequence:
1. White's turn begins (timer starts)
2. Player selects piece to move
3. Valid moves displayed
4. Player selects destination
5. Move validated and executed
6. Check for win/draw conditions
7. Switch turns (timer pauses, other timer starts)
```

### 4.6 Game State Machine

```
States:
┌─────────────┐
│   PLAYING   │ ← Initial state
└──────┬──────┘
       │ Move executed, not in check/mate
       ▼
┌─────────────┐
│    CHECK    │ ← King is in check
└──────┬──────┘
       │ No legal moves available
       ▼
┌─────────────┐
│  CHECKMATE  │ ← Game over (win)
└──────┬──────┘

State Transitions:
PLAYING → CHECK: King in check, legal moves available
PLAYING → STALEMATE: No legal moves, not in check
CHECK → CHECKMATE: King in check, no legal moves
CHECK → PLAYING: Block/check/capture resolves check
ANY → PLAYING: New game started
```

---

## 5. Win/Lose/Draw Conditions

### 5.1 Checkmate

**Definition:** King is in check and no legal moves exist for any piece.

**Detection:**
```
1. King is in check (enemy piece can capture King)
2. For every piece of current player:
   - Generate all possible moves
   - None escape from check
3. Result: CHECKMATE
```

**Outcome:**
- Current player loses
- Opponent wins
- Display: "Checkmate! [Color] wins!"

### 5.2 Stalemate

**Definition:** Current player has no legal moves but is not in check.

**Detection:**
```
1. For every piece of current player:
   - Generate all possible moves
   - All moves are invalid (blocked or illegal)
2. King is NOT in check
3. Result: STALEMATE
```

**Outcome:**
- Draw
- Display: "Stalemate! Game is a draw."

### 5.3 Insufficient Material Draw

**Definition:** Neither player has enough material to checkmate.

**Recognized Patterns:**
| Pattern | White | Black | Result |
|---------|-------|-------|--------|
| K vs K | King only | King only | Draw |
| KB vs K | King + Bishop | King only | Draw |
| KN vs K | King + Knight | King only | Draw |

**Detection:**
```
1. Count remaining pieces (excluding Kings)
2. If no pieces remain: Draw (K vs K)
3. If only 1 piece remains:
   - If Bishop: Draw (KB vs K)
   - If Knight: Draw (KN vs K)
4. Otherwise: Game continues
```

---

## 6. UI Elements Specification

### 6.1 Game Timer

**Display Format:** MM:SS

**Timer Behavior:**
- Paused at game start
- Starts when White makes first move
- Only active player's timer runs
- Pauses during opponent's turn
- Displays elapsed time for both players

**Implementation:**
```python
timer_white = 0  # seconds
timer_black = 0  # seconds
active_timer = 'white'  # or 'black'
game_start_time = None
```

### 6.2 Turn Indicator

**Display:**
- Shows current player's color
- Format: "WHITE's Turn" / "BLACK's Turn"
- Color-coded background highlight

### 6.3 Game Status Display

**Possible States:**
| State | Display Text | Text Color |
|-------|--------------|------------|
| Playing | "Playing" | White (#E8E8E8) |
| Check | "CHECK!" | Red (#FF4444) |
| Checkmate | "Checkmate! White/Black wins!" | Gold (#FFD700) |
| Stalemate | "Stalemate! Draw" | Yellow (#FFFF00) |
| Insufficient Material | "Draw by insufficient material" | Yellow (#FFFF00) |

### 6.4 Captured Pieces Display

**Display Location:**
- White panel: White's captured black pieces
- Black panel: Black's captured white pieces

**Display Format:**
- Horizontal row of piece symbols
- Grouped by type (Queens first, then Rooks, etc.)
- Size: 30 pt font

**Implementation:**
```python
captured_by_white = []  # List of black pieces
captured_by_black = []  # List of white pieces
```

### 6.5 Control Buttons

**Button: New Game**
- Resets entire game
- Clears board to starting position
- Resets both timers to 00:00
- Clears captured pieces
- Sets turn to White

**Button: Reset**
- Resets current game (same as New Game for 2-player)
- Shorthand for "New Game"

---

## 7. User Interactions

### 7.1 Mouse Interactions

| Action | Result |
|--------|--------|
| Click on own piece (on turn) | Select piece, show valid moves |
| Click on valid move square | Execute move |
| Click on different own piece | Change selection |
| Click on invalid square | Deselect current piece |

### 7.2 Visual Feedback

```
Selected Piece:
  - Square border: Gold 3px
  - Valid moves: Green dots/indicators on squares

Hover State:
  - Square: Slight brightness increase

Invalid Selection:
  - No action (or brief red flash)
```

### 7.3 Keyboard Interactions (Optional)

| Key | Action |
|-----|--------|
| N | New game |
| Escape | Deselect piece |

---

## 8. Data Classes

### 8.1 Piece Class

```python
class Piece:
    def __init__(self, color: Color, piece_type: PieceType):
        self.color = color          # WHITE or BLACK
        self.piece_type = piece_type  # KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
        self.has_moved = False     # For castling, en passant

    def __repr__(self):
        symbols = {WHITE: '♔♕♖♗♘♙', BLACK: '♚♛♜♝♞♟'}
        return symbols[self.color][self.piece_type.value]
```

### 8.2 Game State Class

```python
class GameState:
    def __init__(self):
        self.board = [[None]*8 for _ in range(8)]
        self.turn = WHITE
        self.timer_white = 0
        self.timer_black = 0
        self.captured_white = []  # Pieces captured BY black (white pieces lost)
        self.captured_black = []  # Pieces captured BY white (black pieces lost)
        self.last_move = None    # (from_square, to_square)
        self.game_status = PLAYING
        self.check_status = False
```

---

## 9. Edge Cases

### 9.1 Move Validation Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Move exposes King to check | Move rejected |
| Path blocked (sliding pieces) | Move rejected |
| Castle across check | Move rejected |
| Pawn blocked forward | Move rejected |
| En passant after delay | Move rejected (too late) |
| Promotion with no square | N/A (always has square) |

### 9.2 Game State Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 50 moves no capture/pawn | Optional claim draw (not auto) |
| Triple repetition | Optional claim draw (not auto) |
| Both clocks at 0 | Game continues (no auto-lose) |

---

## 10. Performance Requirements

| Metric | Target |
|--------|--------|
| Frame Rate | 60 FPS |
| Move Validation | < 1ms per move |
| Check Detection | < 5ms |
| Memory Usage | < 100 MB |

---

## 11. Acceptance Criteria

### 11.1 Core Functionality

- [ ] Board renders correctly with alternating colors
- [ ] All 32 pieces display in correct starting positions
- [ ] Pieces move according to their movement rules
- [ ] Illegal moves are rejected
- [ ] Turn alternates between White and Black
- [ ] Captured pieces display in appropriate panel
- [ ] Game timers track elapsed time accurately

### 11.2 Special Moves

- [ ] Castling works (both sides, both colors)
- [ ] En passant capture works
- [ ] Pawn promotion occurs at back rank

### 11.3 Win/Draw Detection

- [ ] Check is detected and displayed
- [ ] Checkmate is detected and game ends
- [ ] Stalemate is detected and game ends
- [ ] K vs K draw is detected
- [ ] KB vs K draw is detected
- [ ] KN vs K draw is detected

### 11.4 UI/UX

- [ ] Selected piece highlighted
- [ ] Valid moves indicated
- [ ] Last move visible
- [ ] King in check visually indicated
- [ ] Turn indicator updates correctly
- [ ] Game status displays accurately
- [ ] New Game button resets everything

### 11.5 Visual Checkpoints

1. **Initial State:** All 32 pieces visible, timers at 00:00, turn: White
2. **Mid-Game:** Some pieces moved, captured pieces shown, timers running
3. **Check State:** Red indicator on King, status shows "CHECK!"
4. **End Game:** Status shows winner/draw, no further moves allowed

---

## 12. Future Enhancements (Out of Scope)

These features are NOT required for the initial version but could be added later:

- AI opponent (various difficulty levels)
- Move history / notation display
- Undo/redo functionality
- Save/load games
- Sound effects
- Custom piece sprites
- Network play
- Tournament mode
- Time controls (blitz, rapid, classical)
- FEN/FEN import/export

---

## 13. Appendix

### A. Unicode Chess Symbols Reference

| Code Point | Symbol | Name |
|-----------|--------|------|
| U+2654 | ♔ | White King |
| U+2655 | ♕ | White Queen |
| U+2656 | ♖ | White Rook |
| U+2657 | ♗ | White Bishop |
| U+2658 | ♘ | White Knight |
| U+2659 | ♙ | White Pawn |
| U+265A | ♚ | Black King |
| U+265B | ♛ | Black Queen |
| U+265C | ♜ | Black Rook |
| U+265D | ♝ | Black Bishop |
| U+265E | ♞ | Black Knight |
| U+265F | ♟ | Black Pawn |

### B. Standard Chess Rules Reference

- Game is played between two players on a 8x8 board
- White always moves first
- Objective: Checkmate the opponent's King
- If a King cannot escape capture, game ends
- Draw occurs under specific conditions (stalemate, insufficient material, etc.)

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Author:** Technical Specification