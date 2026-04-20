"""
Chess Manager - A fully-featured 2-player chess game built with Pygame
Complete implementation with all standard chess rules
"""

from __future__ import annotations

import pygame
import sys
from enum import Enum
from typing import List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field


# ==================== CONSTANTS ====================

class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class PieceType(Enum):
    KING = 0
    QUEEN = 1
    ROOK = 2
    BISHOP = 3
    KNIGHT = 4
    PAWN = 5


class GameStatus(Enum):
    PLAYING = "playing"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"


# Unicode chess symbols
WHITE_SYMBOLS = {
    PieceType.KING: '♔',
    PieceType.QUEEN: '♕',
    PieceType.ROOK: '♖',
    PieceType.BISHOP: '♗',
    PieceType.KNIGHT: '♘',
    PieceType.PAWN: '♙',
}

BLACK_SYMBOLS = {
    PieceType.KING: '♚',
    PieceType.QUEEN: '♛',
    PieceType.ROOK: '♜',
    PieceType.BISHOP: '♝',
    PieceType.KNIGHT: '♞',
    PieceType.PAWN: '♟',
}

# Color palette
COLORS = {
    'light_square': (240, 217, 181),      # #F0D9B5
    'dark_square': (181, 136, 99),        # #B58863
    'board_border': (92, 64, 51),         # #5C4033
    'background': (45, 45, 45),           # #2D2D2D
    'ui_panel': (60, 60, 60),              # #3C3C3C
    'ui_border': (74, 74, 74),            # #4A4A4A
    'text_primary': (232, 232, 232),     # #E8E8E8
    'text_secondary': (160, 160, 160),   # #A0A0A0
    'white_turn': (255, 254, 240),        # #FFFEF0
    'black_turn': (26, 26, 26),           # #1A1A1A
    'highlight_selected': (255, 215, 0),  # #FFD700 Gold
    'highlight_valid': (0, 170, 0),       # #00AA00
    'highlight_last': (255, 255, 0),    # Yellow
    'check_indicator': (255, 68, 68),    # #FF4444
    'button_bg': (74, 106, 138),          # #4A6A8A
    'button_hover': (90, 122, 154),      # #5A7A9A
}

# Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BOARD_SIZE = 560
SQUARE_SIZE = 70
BOARD_BORDER = 10
UI_PANEL_WIDTH = 300


# ==================== DATA CLASSES ====================

@dataclass
class Piece:
    color: Color
    piece_type: PieceType
    has_moved: bool = False

    def get_symbol(self) -> str:
        if self.color == Color.WHITE:
            return WHITE_SYMBOLS[self.piece_type]
        else:
            return BLACK_SYMBOLS[self.piece_type]

    def __repr__(self):
        return self.get_symbol()


@dataclass
class Move:
    from_x: int
    from_y: int
    to_x: int
    to_y: int
    is_castling: bool = False
    castling_type: str = ""  # "kingside" or "queenside"
    is_en_passant: bool = False
    is_promotion: bool = False
    promotion_piece: PieceType = PieceType.QUEEN

    def __repr__(self):
        return f"{chr(97 + self.from_x)}{8 - self.from_y} -> {chr(97 + self.to_x)}{8 - self.to_y}"


@dataclass
class GameState:
    board: list = field(default_factory=lambda: [[None] * 8 for _ in range(8)])
    turn: Color = Color.WHITE
    timer_white: int = 0  # seconds
    timer_black: int = 0  # seconds
    captured_white: list = field(default_factory=list)  # White pieces captured by black
    captured_black: list = field(default_factory=list)  # Black pieces captured by white
    last_move: Any = None
    game_status: GameStatus = GameStatus.PLAYING
    in_check: bool = False
    selected_square: Any = None
    legal_moves: list = field(default_factory=list)
    en_passant_target: Any = None  # Square behind pawn that can be captured en passant


# ==================== GAME LOGIC ====================

class ChessGame:
    def __init__(self):
        self.game_state = GameState()
        self.setup_board()
        self.game_started = False
        self.current_timer = None

    def setup_board(self):
        """Set up the initial board position"""
        # Clear board
        self.game_state.board = [[None] * 8 for _ in range(8)]

        # Place pawns
        for col in range(8):
            self.game_state.board[col][1] = Piece(Color.WHITE, PieceType.PAWN)
            self.game_state.board[col][6] = Piece(Color.BLACK, PieceType.PAWN)

        # Place rooks
        self.game_state.board[0][0] = Piece(Color.WHITE, PieceType.ROOK)
        self.game_state.board[7][0] = Piece(Color.WHITE, PieceType.ROOK)
        self.game_state.board[0][7] = Piece(Color.BLACK, PieceType.ROOK)
        self.game_state.board[7][7] = Piece(Color.BLACK, PieceType.ROOK)

        # Place knights
        self.game_state.board[1][0] = Piece(Color.WHITE, PieceType.KNIGHT)
        self.game_state.board[6][0] = Piece(Color.WHITE, PieceType.KNIGHT)
        self.game_state.board[1][7] = Piece(Color.BLACK, PieceType.KNIGHT)
        self.game_state.board[6][7] = Piece(Color.BLACK, PieceType.KNIGHT)

        # Place bishops
        self.game_state.board[2][0] = Piece(Color.WHITE, PieceType.BISHOP)
        self.game_state.board[5][0] = Piece(Color.WHITE, PieceType.BISHOP)
        self.game_state.board[2][7] = Piece(Color.BLACK, PieceType.BISHOP)
        self.game_state.board[5][7] = Piece(Color.BLACK, PieceType.BISHOP)

        # Place queens
        self.game_state.board[3][0] = Piece(Color.WHITE, PieceType.QUEEN)
        self.game_state.board[3][7] = Piece(Color.BLACK, PieceType.QUEEN)

        # Place kings
        self.game_state.board[4][0] = Piece(Color.WHITE, PieceType.KING)
        self.game_state.board[4][7] = Piece(Color.BLACK, PieceType.KING)

    def find_king(self, color: Color) -> Tuple[int, int]:
        """Find the king's position"""
        for x in range(8):
            for y in range(8):
                piece = self.game_state.board[x][y]
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return (x, y)
        return (-1, -1)

    def is_square_attacked(self, x: int, y: int, by_color: Color) -> bool:
        """Check if a square is attacked by any piece of the given color"""
        opponent = by_color
        # Check pawn attacks
        pawn_direction = -1 if opponent == Color.WHITE else 1
        pawn_y = y + pawn_direction
        for dx in [-1, 1]:
            nx, ny = x + dx, pawn_y
            if 0 <= nx < 8 and 0 <= ny < 8:
                piece = self.game_state.board[nx][ny]
                if piece and piece.color == opponent and piece.piece_type == PieceType.PAWN:
                    return True

        # Check knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dx, dy in knight_moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                piece = self.game_state.board[nx][ny]
                if piece and piece.color == opponent and piece.piece_type == PieceType.KNIGHT:
                    return True

        # Check king attacks
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    piece = self.game_state.board[nx][ny]
                    if piece and piece.color == opponent and piece.piece_type == PieceType.KING:
                        return True

        # Check sliding piece attacks (queen, rook, bishop)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Straight
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # Diagonal
        ]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                piece = self.game_state.board[nx][ny]
                if piece and piece.color == opponent:
                    if piece.piece_type in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP]:
                        # Determine if sliding piece can attack
                        if (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            if piece.piece_type in [PieceType.QUEEN, PieceType.ROOK]:
                                return True
                        else:
                            if piece.piece_type in [PieceType.QUEEN, PieceType.BISHOP]:
                                return True
                    break
                nx, ny = nx + dx, ny + dy

        return False

    def is_in_check(self, color: Color) -> bool:
        """Check if the king of the given color is in check"""
        king_pos = self.find_king(color)
        if king_pos == (-1, -1):
            return False
        king_x, king_y = king_pos
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(king_x, king_y, opponent)

    def is_path_clear(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if path is clear for sliding pieces"""
        dx = 0 if x1 == x2 else (1 if x2 > x1 else -1)
        dy = 0 if y1 == y2 else (1 if y2 > y1 else -1)

        x, y = x1 + dx, y1 + dy
        while (x, y) != (x2, y2):
            if self.game_state.board[x][y] is not None:
                return False
            x, y = x + dx, y + dy
        return True

    def get_pseudo_legal_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all pseudo-legal moves for a piece (ignoring check)"""
        piece = self.game_state.board[x][y]
        if piece is None:
            return []

        moves = []
        color = piece.color
        piece_type = piece.piece_type

        if piece_type == PieceType.PAWN:
            # Pawn direction (white moves up/forward toward rank 8, black moves down toward rank 1)
            direction = -1 if color == Color.BLACK else 1
            start_row = 1 if color == Color.WHITE else 6

            # Forward move
            if 0 <= y + direction < 8 and self.game_state.board[x][y + direction] is None:
                moves.append((x, y + direction))
                # Double move from starting position
                if y == start_row and 0 <= y + 2 * direction < 8:
                    if self.game_state.board[x][y + 2 * direction] is None:
                        moves.append((x, y + 2 * direction))

            # Captures
            for dx in [-1, 1]:
                nx, ny = x + dx, y + direction
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = self.game_state.board[nx][ny]
                    if target and target.color != color:
                        moves.append((nx, ny))

            # En passant
            if self.game_state.en_passant_target:
                ep_x, ep_y = self.game_state.en_passant_target
                if y == ep_y and abs(x - ep_x) == 1:
                    moves.append((ep_x, ep_y))

        elif piece_type == PieceType.KNIGHT:
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dx, dy in knight_moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    target = self.game_state.board[nx][ny]
                    if target is None or target.color != color:
                        moves.append((nx, ny))

        elif piece_type == PieceType.KING:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 8 and 0 <= ny < 8:
                        target = self.game_state.board[nx][ny]
                        if target is None or target.color != color:
                            moves.append((nx, ny))

            # Castling (only if king hasn't moved)
            if not piece.has_moved and not self.is_in_check(color):
                # Kingside castling
                if color == Color.WHITE:
                    # Check kingside
                    rook = self.game_state.board[7][0]
                    if rook and rook.piece_type == PieceType.ROOK and not rook.has_moved:
                        if self.game_state.board[5][0] is None and self.game_state.board[6][0] is None:
                            if not self.is_square_attacked(5, 0, Color.BLACK) and not self.is_square_attacked(6, 0, Color.BLACK):
                                moves.append((6, 0))
                    # Queenside castling
                    rook = self.game_state.board[0][0]
                    if rook and rook.piece_type == PieceType.ROOK and not rook.has_moved:
                        if self.game_state.board[1][0] is None and self.game_state.board[2][0] is None and self.game_state.board[3][0] is None:
                            if not self.is_square_attacked(3, 0, Color.BLACK) and not self.is_square_attacked(2, 0, Color.BLACK):
                                moves.append((2, 0))
                else:
                    # Black kingside
                    rook = self.game_state.board[7][7]
                    if rook and rook.piece_type == PieceType.ROOK and not rook.has_moved:
                        if self.game_state.board[5][7] is None and self.game_state.board[6][7] is None:
                            if not self.is_square_attacked(5, 7, Color.WHITE) and not self.is_square_attacked(6, 7, Color.WHITE):
                                moves.append((6, 7))
                    # Queenside castling
                    rook = self.game_state.board[0][7]
                    if rook and rook.piece_type == PieceType.ROOK and not rook.has_moved:
                        if self.game_state.board[1][7] is None and self.game_state.board[2][7] is None and self.game_state.board[3][7] is None:
                            if not self.is_square_attacked(3, 7, Color.WHITE) and not self.is_square_attacked(2, 7, Color.WHITE):
                                moves.append((2, 7))

        else:  # Queen, Rook, Bishop
            directions = []
            if piece_type in [PieceType.QUEEN, PieceType.ROOK]:
                directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])
            if piece_type in [PieceType.QUEEN, PieceType.BISHOP]:
                directions.extend([(-1, -1), (1, -1), (-1, 1), (1, 1)])

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while 0 <= nx < 8 and 0 <= ny < 8:
                    target = self.game_state.board[nx][ny]
                    if target is None:
                        moves.append((nx, ny))
                    else:
                        if target.color != color:
                            moves.append((nx, ny))
                        break
                    nx, ny = nx + dx, ny + dy

        return moves

    def is_legal_move(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if a move is legal (doesn't leave king in check)"""
        piece = self.game_state.board[from_x][from_y]
        if piece is None:
            return False

        color = piece.color

        # Save current state
        original_target = self.game_state.board[to_x][to_y]
        original_source = self.game_state.board[from_x][from_y]

        # Make move temporarily
        self.game_state.board[to_x][to_y] = original_source
        self.game_state.board[from_x][from_y] = None

        # Handle en passant
        en_passant_capture = None
        if piece.piece_type == PieceType.PAWN and self.game_state.en_passant_target:
            ep_x, ep_y = self.game_state.en_passant_target
            if to_x == ep_x and to_y == ep_y:
                captured_pawn_y = from_y
                en_passant_capture = self.game_state.board[to_x][captured_pawn_y]
                self.game_state.board[to_x][captured_pawn_y] = None

        # Check if king is in check
        in_check = self.is_in_check(color)

        # Restore state
        self.game_state.board[from_x][from_y] = original_source
        self.game_state.board[to_x][to_y] = original_target
        if en_passant_capture:
            self.game_state.board[to_x][captured_pawn_y] = en_passant_capture

        return not in_check

    def get_legal_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece"""
        piece = self.game_state.board[x][y]
        if piece is None:
            return []

        pseudo_moves = self.get_pseudo_legal_moves(x, y)
        legal_moves = []

        for to_x, to_y in pseudo_moves:
            if self.is_legal_move(x, y, to_x, to_y):
                legal_moves.append((to_x, to_y))

        return legal_moves

    def has_any_legal_move(self, color: Color) -> bool:
        """Check if a player has any legal move"""
        for x in range(8):
            for y in range(8):
                piece = self.game_state.board[x][y]
                if piece and piece.color == color:
                    if self.get_legal_moves(x, y):
                        return True
        return False

    def make_move(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Execute a move"""
        piece = self.game_state.board[from_x][from_y]
        if piece is None:
            return False

        color = piece.color

        # Save en passant target before move
        self.game_state.en_passant_target = None

        # Handle castling
        if piece.piece_type == PieceType.KING and abs(to_x - from_x) == 2:
            if to_x > from_x:  # Kingside
                rook = self.game_state.board[7][from_y]
                self.game_state.board[6][from_y] = rook
                self.game_state.board[7][from_y] = None
                if rook:
                    rook.has_moved = True
            else:  # Queenside
                rook = self.game_state.board[0][from_y]
                self.game_state.board[2][from_y] = rook
                self.game_state.board[0][from_y] = None
                if rook:
                    rook.has_moved = True
            piece.has_moved = True
        else:
            # Handle en passant
            if piece.piece_type == PieceType.PAWN:
                # Check if this is an en passant capture
                if self.game_state.en_passant_target:
                    ep_x, ep_y = self.game_state.en_passant_target
                    if to_x == ep_x and to_y == ep_y:
                        captured_pawn_y = from_y
                        captured_pawn = self.game_state.board[ep_x][captured_pawn_y]
                        self.game_state.board[ep_x][captured_pawn_y] = None
                        # Add to captured pieces
                        if color == Color.WHITE:
                            self.game_state.captured_black.append(captured_pawn)
                        else:
                            self.game_state.captured_white.append(captured_pawn)

                # Set en passant target if pawn moves 2 squares
                if abs(to_y - from_y) == 2:
                    self.game_state.en_passant_target = (from_x, (from_y + to_y) // 2)

            # Move piece
            target_piece = self.game_state.board[to_x][to_y]
            if target_piece:
                if color == Color.WHITE:
                    self.game_state.captured_black.append(target_piece)
                else:
                    self.game_state.captured_white.append(target_piece)

            self.game_state.board[to_x][to_y] = piece
            self.game_state.board[from_x][from_y] = None

            # Handle promotion
            if piece.piece_type == PieceType.PAWN:
                if (color == Color.WHITE and to_y == 7) or (color == Color.BLACK and to_y == 0):
                    piece.piece_type = PieceType.QUEEN

            piece.has_moved = True

        # Store last move
        self.game_state.last_move = ((from_x, from_y), (to_x, to_y))

        # Mark game as started when first move is made
        self.game_started = True

        return True

    def check_game_status(self):
        """Check game status (check, checkmate, stalemate, insufficient material)"""
        current_player = self.game_state.turn

        # Check if in check
        if self.is_in_check(current_player):
            self.game_state.in_check = True
            # Check if checkmate
            if not self.has_any_legal_move(current_player):
                self.game_state.game_status = GameStatus.CHECKMATE
                return
        else:
            self.game_state.in_check = False
            # Check if stalemate
            if not self.has_any_legal_move(current_player):
                self.game_state.game_status = GameStatus.STALEMATE
                return

        # Check insufficient material
        white_pieces = []
        black_pieces = []
        for x in range(8):
            for y in range(8):
                piece = self.game_state.board[x][y]
                if piece:
                    if piece.color == Color.WHITE:
                        white_pieces.append(piece.piece_type)
                    else:
                        black_pieces.append(piece.piece_type)

        # King vs King
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            self.game_state.game_status = GameStatus.INSUFFICIENT_MATERIAL
            return

        # KB vs K or KN vs K (either side)
        if (len(white_pieces) == 1 and len(black_pieces) == 1) or \
           (len(white_pieces) == 1 and len(black_pieces) == 2) or \
           (len(white_pieces) == 2 and len(black_pieces) == 1):
            only_white = white_pieces[0] if white_pieces else None
            only_black = black_pieces[0] if black_pieces else None
            if only_white in [PieceType.BISHOP, PieceType.KNIGHT] or only_black in [PieceType.BISHOP, PieceType.KNIGHT]:
                self.game_state.game_status = GameStatus.INSUFFICIENT_MATERIAL
                return

        self.game_state.game_status = GameStatus.PLAYING

    def switch_turn(self):
        """Switch turns"""
        self.game_state.turn = Color.BLACK if self.game_state.turn == Color.WHITE else Color.WHITE

    def select_square(self, x: int, y: int):
        """Select a square"""
        piece = self.game_state.board[x][y]

        # If clicking on own piece, select it
        if piece and piece.color == self.game_state.turn:
            self.game_state.selected_square = (x, y)
            self.game_state.legal_moves = self.get_legal_moves(x, y)
        else:
            # Check if clicking on valid move
            if self.game_state.selected_square and (x, y) in self.game_state.legal_moves:
                from_x, from_y = self.game_state.selected_square
                if self.make_move(from_x, from_y, x, y):
                    self.game_state.selected_square = None
                    self.game_state.legal_moves = []

                    # Check game status
                    self.check_game_status()

                    # Switch turns if game is still playing
                    if self.game_state.game_status == GameStatus.PLAYING:
                        self.switch_turn()
            else:
                # Deselect
                self.game_state.selected_square = None
                self.game_state.legal_moves = []

    def reset_game(self):
        """Reset the game"""
        self.game_state = GameState()
        self.setup_board()
        self.game_started = False
        self.current_timer = None


# ==================== RENDERING ====================

class ChessRenderer:
    def __init__(self, game: ChessGame, screen: pygame.Surface):
        self.game = game
        self.screen = screen
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_mono = None
        self.init_fonts()

    def init_fonts(self):
        """Initialize fonts"""
        # Try to use system fonts, fallback to default
        try:
            self.font_large = pygame.font.SysFont('segoe symbol', 50)
            self.font_medium = pygame.font.SysFont('segoe symbol', 30)
            self.font_small = pygame.font.SysFont('segoe symbol', 24)
        except:
            self.font_large = pygame.font.Font(None, 50)
            self.font_medium = pygame.font.Font(None, 30)
            self.font_small = pygame.font.Font(None, 24)

        self.font_mono = pygame.font.SysFont('consolas', 24)
        if not self.font_mono:
            self.font_mono = pygame.font.Font(None, 24)

    def draw_board(self):
        """Draw the chess board"""
        board_x = 50
        board_y = 50

        # Draw border
        border_rect = pygame.Rect(board_x - BOARD_BORDER, board_y - BOARD_BORDER,
                               BOARD_SIZE + 2 * BOARD_BORDER, BOARD_SIZE + 2 * BOARD_BORDER)
        pygame.draw.rect(self.screen, COLORS['board_border'], border_rect)

        # Draw squares
        for x in range(8):
            for y in range(8):
                color = COLORS['light_square'] if (x + y) % 2 == 0 else COLORS['dark_square']
                rect = pygame.Rect(board_x + x * SQUARE_SIZE, board_y + y * SQUARE_SIZE,
                                  SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        """Draw chess pieces"""
        board_x = 50
        board_y = 50

        for x in range(8):
            for y in range(8):
                piece = self.game.game_state.board[x][y]
                if piece:
                    symbol = piece.get_symbol()
                    color = COLORS['text_primary'] if piece.color == Color.WHITE else COLORS['black_turn']

                    # Render text
                    text = self.font_large.render(symbol, True, color)
                    text_rect = text.get_rect(center=(board_x + x * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                       board_y + y * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text, text_rect)

    def draw_highlights(self):
        """Draw highlights for selected piece, legal moves, etc."""
        board_x = 50
        board_y = 50

        # Highlight last move
        if self.game.game_state.last_move:
            (from_x, from_y), (to_x, to_y) = self.game.game_state.last_move
            for sq_x, sq_y in [(from_x, from_y), (to_x, to_y)]:
                highlight_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surf, (255, 255, 0, 77), highlight_surf.get_rect())
                self.screen.blit(highlight_surf, (board_x + sq_x * SQUARE_SIZE, board_y + sq_y * SQUARE_SIZE))

        # Highlight selected square
        if self.game.game_state.selected_square:
            sel_x, sel_y = self.game.game_state.selected_square
            rect = pygame.Rect(board_x + sel_x * SQUARE_SIZE, board_y + sel_y * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(self.screen, COLORS['highlight_selected'], rect, 3)

        # Highlight legal moves
        for to_x, to_y in self.game.game_state.legal_moves:
            target = self.game.game_state.board[to_x][to_y]
            center_x = board_x + to_x * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = board_y + to_y * SQUARE_SIZE + SQUARE_SIZE // 2

            if target:  # Capture
                pygame.draw.circle(self.screen, COLORS['highlight_selected'], (center_x, center_y), 25, 3)
            else:  # Normal move
                pygame.draw.circle(self.screen, COLORS['highlight_valid'], (center_x, center_y), 12)

        # Highlight king in check
        if self.game.game_state.in_check:
            king_pos = self.game.find_king(self.game.game_state.turn)
            if king_pos != (-1, -1):
                king_x, king_y = king_pos
                rect = pygame.Rect(board_x + king_x * SQUARE_SIZE, board_y + king_y * SQUARE_SIZE,
                                  SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, COLORS['check_indicator'], rect, 4)

    def draw_coordinates(self):
        """Draw file and rank labels"""
        board_x = 50
        board_y = 50

        # Files (a-h)
        for i in range(8):
            label = chr(97 + i)  # 'a' to 'h'
            text = self.font_small.render(label, True, COLORS['text_secondary'])
            text_rect = text.get_rect(center=(board_x + i * SQUARE_SIZE + SQUARE_SIZE // 2,
                                              board_y - 20))
            self.screen.blit(text, text_rect)

        # Ranks (1-8)
        for i in range(8):
            label = str(8 - i)  # '1' to '8'
            text = self.font_small.render(label, True, COLORS['text_secondary'])
            text_rect = text.get_rect(center=(board_x - 20, board_y + i * SQUARE_SIZE + SQUARE_SIZE // 2))
            self.screen.blit(text, text_rect)

    def format_time(self, seconds: int) -> str:
        """Format time as MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def draw_ui_panel(self):
        """Draw the UI panel"""
        panel_x = 650

        # Panel background
        panel_rect = pygame.Rect(panel_x, 20, 290, 760)
        pygame.draw.rect(self.screen, COLORS['ui_panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['ui_border'], panel_rect, 2)

        # White player panel (top)
        self.draw_player_panel(panel_x + 20, 40, Color.WHITE, "WHITE")

        # Status panel (middle)
        self.draw_status_panel(panel_x + 20, 240)

        # Black player panel (bottom)
        self.draw_player_panel(panel_x + 20, 380, Color.BLACK, "BLACK")

    def draw_player_panel(self, x: int, y: int, color: Color, name: str):
        """Draw a player's info panel"""
        panel_bg = pygame.Rect(x, y, 250, 140)
        pygame.draw.rect(self.screen, COLORS['ui_panel'], panel_bg)
        pygame.draw.rect(self.screen, COLORS['ui_border'], panel_bg, 1)

        # Player name
        text_color = COLORS['text_primary']
        name_text = self.font_medium.render(name, True, text_color)
        self.screen.blit(name_text, (x + 10, y + 10))

        # Timer
        timer = self.game.game_state.timer_white if color == Color.WHITE else self.game.game_state.timer_black
        timer_text = self.font_mono.render(f"Timer: {self.format_time(timer)}", True, text_color)
        self.screen.blit(timer_text, (x + 10, y + 40))

        # Captured pieces
        captured_label = self.font_small.render("Captured:", True, COLORS['text_secondary'])
        self.screen.blit(captured_label, (x + 10, y + 70))

        captured_list = self.game.game_state.captured_black if color == Color.WHITE else self.game.game_state.captured_white
        if captured_list:
            # Sort by piece type value
            captured_list.sort(key=lambda p: p.piece_type.value, reverse=True)
            symbols = " ".join([p.get_symbol() for p in captured_list])
            captured_text = self.font_medium.render(symbols, True, COLORS['text_primary'])
            self.screen.blit(captured_text, (x + 10, y + 95))
        else:
            none_text = self.font_small.render("None", True, COLORS['text_secondary'])
            self.screen.blit(none_text, (x + 80, y + 95))

    def draw_status_panel(self, x: int, y: int):
        """Draw status panel"""
        panel_bg = pygame.Rect(x, y, 250, 110)
        pygame.draw.rect(self.screen, COLORS['ui_panel'], panel_bg)
        pygame.draw.rect(self.screen, COLORS['ui_border'], panel_bg, 1)

        # Turn indicator
        turn_text = self.game.game_state.turn.name + "'s Turn"
        turn_color = COLORS['white_turn'] if self.game.game_state.turn == Color.WHITE else COLORS['black_turn']
        turn_display = self.font_medium.render(turn_text, True, turn_color)
        self.screen.blit(turn_display, (x + 10, y + 10))

        # Game status
        status = self.game.game_state.game_status
        if status == GameStatus.PLAYING:
            status_text = "Playing"
            status_color = COLORS['text_primary']
        elif status == GameStatus.CHECK:
            status_text = "CHECK!"
            status_color = COLORS['check_indicator']
        elif status == GameStatus.CHECKMATE:
            winner = "White" if self.game.game_state.turn == Color.BLACK else "Black"
            status_text = f"Checkmate! {winner} wins!"
            status_color = COLORS['highlight_selected']
        elif status == GameStatus.STALEMATE:
            status_text = "Stalemate! Draw"
            status_color = COLORS['highlight_last']
        elif status == GameStatus.INSUFFICIENT_MATERIAL:
            status_text = "Draw - Insufficient Material"
            status_color = COLORS['highlight_last']

        status_display = self.font_small.render(status_text, True, status_color)
        self.screen.blit(status_display, (x + 10, y + 45))

        # Buttons
        self.draw_button(x + 10, y + 70, "New Game", "new_game")

    def draw_button(self, x: int, y: int, label: str, action: str):
        """Draw a button"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, 100, 30)

        # Check hover
        is_hover = button_rect.collidepoint(mouse_pos)
        bg_color = COLORS['button_hover'] if is_hover else COLORS['button_bg']

        pygame.draw.rect(self.screen, bg_color, button_rect)
        pygame.draw.rect(self.screen, COLORS['ui_border'], button_rect, 1)

        text = self.font_small.render(label, True, COLORS['text_primary'])
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)

    def render(self):
        """Render the game"""
        # Fill background
        self.screen.fill(COLORS['background'])

        # Draw board
        self.draw_board()
        self.draw_coordinates()
        self.draw_pieces()
        self.draw_highlights()

        # Draw UI
        self.draw_ui_panel()


# ==================== MAIN ====================

def main():
    """Main function"""
    pygame.init()
    pygame.display.set_caption("Chess Manager")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    game = ChessGame()
    renderer = ChessRenderer(game, screen)

    clock = pygame.time.Clock()

    running = True
    while running:
        # Update timer
        if game.game_started and game.game_state.game_status == GameStatus.PLAYING:
            if game.game_state.turn == Color.WHITE:
                game.game_state.timer_white += 1
                game.current_timer = 'white'
            else:
                game.game_state.timer_black += 1
                game.current_timer = 'black'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Board click
                board_x = 50
                board_y = 50
                if board_x <= mouse_pos[0] < board_x + BOARD_SIZE and \
                   board_y <= mouse_pos[1] < board_y + BOARD_SIZE:
                    x = (mouse_pos[0] - board_x) // SQUARE_SIZE
                    y = (mouse_pos[1] - board_y) // SQUARE_SIZE
                    game.select_square(x, y)

                # Button clicks
                panel_x = 650
                mouse_x = mouse_pos[0] - panel_x - 20 - 10
                mouse_y = mouse_pos[1] - 240 - 70

                if 10 <= mouse_x <= 110 and 70 <= mouse_y <= 100:
                    game.reset_game()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.game_state.selected_square = None
                    game.game_state.legal_moves = []

        # Render
        renderer.render()
        pygame.display.flip()

        # Cap frame rate and timer update
        clock.tick(1)  # 1 tick per second for timer

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()