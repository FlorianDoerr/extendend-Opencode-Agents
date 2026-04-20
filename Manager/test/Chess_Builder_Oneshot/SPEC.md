# Chess Game Specification

## Project Overview
- **Project name**: Pygame Chess
- **Type**: Desktop game
- **Core functionality**: A fully functional chess game with visual board, piece sprites, move validation, timer, and win detection
- **Target users**: Chess enthusiasts who want to play against another human locally

## UI/UX Specification

### Layout Structure
- **Main window**: 800x700 pixels
- **Chess board**: 640x640 pixels (centered)
- **Info panel**: Right side, 160px wide, showing captured pieces and timer
- **Board orientation**: White at bottom, black at top (standard)

### Visual Design
- **Background color**: #2C2C2C (dark charcoal)
- **Board light squares**: #EEEED2 (cream)
- **Board dark squares**: #769656 (forest green)
- **Highlight color**: #FFFF00 with 50% opacity (yellow highlight for selected piece)
- **Valid move indicator**: Circle with #00FF00 at 40% opacity
- **Font**: Arial, 16px for UI text

### Chess Pieces
- Use Unicode chess symbols rendered as text on the board
- White pieces: ♔♕♖♗♘♙
- Black pieces: ♚♛♜♝♞♟
- Piece size: 70x70 pixels centered in each square

### Components
- **Chess board**: 8x8 grid with alternating colors
- **Timer display**: Minutes:Seconds format for each player
- **Captured pieces panel**: Shows eliminated pieces sorted by type
- **Game status**: Displays check, checkmate, stalemate, or winner

## Functionality Specification

### Core Features
1. **Board initialization**: Standard starting position
2. **Piece selection**: Click to select a piece, highlight valid moves
3. **Move validation**: Only allow legal chess moves for each piece type
4. **Capture handling**: Remove captured pieces from board
5. **Move execution**: Update board state after valid move
6. **Turn tracking**: Alternate between white and black
7. **Timer**: Count up elapsed time for each player
8. **Captured pieces display**: Show all captured pieces
9. **Win detection**: Checkmate detection
10. **Draw detection**: Stalemate and insufficient material

### Piece Movement Rules
- **Pawn**: Forward 1 (or 2 from start), diagonal capture, en passant
- **Rook**: Horizontal/vertical any distance
- **Knight**: L-shape (2+1), can jump over pieces
- **Bishop**: Diagonal any distance
- **Queen**: Horizontal/vertical/diagonal any distance
- **King**: One square any direction, castling (kingside/queenside)

### Special Rules
- **Castling**: King moves 2 squares, rook moves adjacent, no check in between
- **En passant**: Pawn captures pawn that just moved 2 squares
- **Pawn promotion**: Auto-promote to queen on reaching last rank

### Win Conditions
- **Checkmate**: King in check with no legal moves
- **Stalemate**: No legal moves but not in check
- **Insufficient material**: K vs K, K+B vs K, K+N vs K

## Acceptance Criteria
1. Board displays correctly with all pieces in starting position
2. Clicking a piece highlights it and shows valid moves
3. Only legal moves are allowed (no illegal placements)
4. Captured pieces appear in the captured panel
5. Timer increments while player's turn is active
6. Game detects checkmate and declares winner
7. Game detects stalemate as draw
8. All piece types move according to chess rules