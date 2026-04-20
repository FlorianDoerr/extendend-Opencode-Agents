import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
INFO_PANEL_WIDTH = 160

WHITE = (238, 238, 210)
BLACK = (118, 150, 86)
HIGHLIGHT = (255, 255, 0, 128)
VALID_MOVE = (0, 255, 0, 102)
BG_COLOR = (44, 44, 44)

WHITE_PIECES = {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'}
BLACK_PIECES = {'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'}

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chess")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 36)
        self.small_font = pygame.font.SysFont('arial', 16)
        
        self.board = self.create_initial_board()
        self.selected_square = None
        self.valid_moves = []
        self.turn = 'white'
        self.white_time = 0
        self.black_time = 0
        self.last_update = pygame.time.get_ticks()
        self.game_over = False
        self.winner = None
        self.captured_white = []
        self.captured_black = []
        
        self.castling_rights = {
            'white_kingside': True, 'white_queenside': True,
            'black_kingside': True, 'black_queenside': True
        }
        self.en_passant_target = None
        self.move_history = []
        
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rooks_moved = {'kingside': False, 'queenside': False}
        self.black_rooks_moved = {'kingside': False, 'queenside': False}

    def create_initial_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        board[0] = [('black', 'R'), ('black', 'N'), ('black', 'B'), ('black', 'Q'), 
                    ('black', 'K'), ('black', 'B'), ('black', 'N'), ('black', 'R')]
        board[1] = [('black', 'P')] * 8
        board[6] = [('white', 'P')] * 8
        board[7] = [('white', 'R'), ('white', 'N'), ('white', 'B'), ('white', 'Q'), 
                    ('white', 'K'), ('white', 'B'), ('white', 'N'), ('white', 'R')]
        return board

    def draw_board(self):
        self.screen.fill(BG_COLOR)
        
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else BLACK
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                
                if self.selected_square == (row, col):
                    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(highlight_surface, HIGHLIGHT, highlight_surface.get_rect())
                    self.screen.blit(highlight_surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                if (row, col) in self.valid_moves:
                    center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    pygame.draw.circle(self.screen, VALID_MOVE, center, SQUARE_SIZE // 4)
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    color, piece_type = piece
                    symbol = WHITE_PIECES[piece_type] if color == 'white' else BLACK_PIECES[piece_type]
                    text = self.font.render(symbol, True, (255, 255, 255) if color == 'white' else (0, 0, 0))
                    text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                                      row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text, text_rect)

    def draw_info_panel(self):
        panel_x = BOARD_SIZE
        
        pygame.draw.rect(self.screen, (60, 60, 60), (panel_x, 0, INFO_PANEL_WIDTH, SCREEN_HEIGHT))
        
        white_label = self.small_font.render("White", True, (255, 255, 255))
        self.screen.blit(white_label, (panel_x + 20, 20))
        
        white_time = self.format_time(self.white_time)
        white_time_text = self.small_font.render(white_time, True, (255, 255, 255))
        self.screen.blit(white_time_text, (panel_x + 20, 40))
        
        black_label = self.small_font.render("Black", True, (255, 255, 255))
        self.screen.blit(black_label, (panel_x + 20, 100))
        
        black_time = self.format_time(self.black_time)
        black_time_text = self.small_font.render(black_time, True, (255, 255, 255))
        self.screen.blit(black_time_text, (panel_x + 20, 120))
        
        captured_label = self.small_font.render("Captured:", True, (200, 200, 200))
        self.screen.blit(captured_label, (panel_x + 20, 170))
        
        y_offset = 195
        for piece in self.captured_white:
            symbol = WHITE_PIECES[piece]
            text = self.small_font.render(symbol, True, (255, 255, 255))
            self.screen.blit(text, (panel_x + 30, y_offset))
            y_offset += 20
        
        y_offset += 20
        for piece in self.captured_black:
            symbol = BLACK_PIECES[piece]
            text = self.small_font.render(symbol, True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 30, y_offset))
            y_offset += 20
        
        if self.game_over:
            result_text = self.small_font.render(f"{self.winner} wins!", True, (255, 100, 100))
            self.screen.blit(result_text, (panel_x + 20, 550))
        
        turn_text = self.small_font.render(f"Turn: {self.turn.capitalize()}", True, (255, 255, 255))
        self.screen.blit(turn_text, (panel_x + 20, 80))

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_piece_at(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def is_own_piece(self, row, col, color):
        piece = self.get_piece_at(row, col)
        return piece and piece[0] == color

    def is_enemy_piece(self, row, col, color):
        piece = self.get_piece_at(row, col)
        return piece and piece[0] != color

    def is_empty(self, row, col):
        return self.get_piece_at(row, col) is None

    def get_valid_moves(self, row, col):
        piece = self.get_piece_at(row, col)
        if not piece:
            return []
        
        color, piece_type = piece
        moves = []
        
        if piece_type == 'P':
            moves = self.get_pawn_moves(row, col, color)
        elif piece_type == 'R':
            moves = self.get_rook_moves(row, col, color)
        elif piece_type == 'N':
            moves = self.get_knight_moves(row, col, color)
        elif piece_type == 'B':
            moves = self.get_bishop_moves(row, col, color)
        elif piece_type == 'Q':
            moves = self.get_queen_moves(row, col, color)
        elif piece_type == 'K':
            moves = self.get_king_moves(row, col, color)
        
        return [m for m in moves if self.does_not_leave_king_in_check(row, col, m[0], m[1], color)]

    def get_pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        if self.is_empty(row + direction, col):
            moves.append((row + direction, col))
            if row == start_row and self.is_empty(row + 2 * direction, col):
                moves.append((row + 2 * direction, col))
        
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                if self.is_enemy_piece(new_row, new_col, color):
                    moves.append((new_row, new_col))
        
        if self.en_passant_target:
            ep_row, ep_col = self.en_passant_target
            if ep_row == row and abs(ep_col - col) == 1:
                moves.append((ep_row + direction, ep_col))
        
        return moves

    def get_rook_moves(self, row, col, color):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                if self.is_empty(new_row, new_col):
                    moves.append((new_row, new_col))
                elif self.is_enemy_piece(new_row, new_col, color):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        return moves

    def get_knight_moves(self, row, col, color):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_own_piece(new_row, new_col, color):
                    moves.append((new_row, new_col))
        return moves

    def get_bishop_moves(self, row, col, color):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                if self.is_empty(new_row, new_col):
                    moves.append((new_row, new_col))
                elif self.is_enemy_piece(new_row, new_col, color):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        return moves

    def get_queen_moves(self, row, col, color):
        return self.get_rook_moves(row, col, color) + self.get_bishop_moves(row, col, color)

    def get_king_moves(self, row, col, color):
        moves = []
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_own_piece(new_row, new_col, color):
                    moves.append((new_row, new_col))
        
        if not self.is_in_check(color):
            if color == 'white' and row == 7 and col == 4:
                if self.castling_rights['white_kingside'] and self.is_empty(7, 5) and self.is_empty(7, 6):
                    if not self.is_square_attacked(7, 5, 'black') and not self.is_square_attacked(7, 6, 'black'):
                        moves.append((7, 6))
                if self.castling_rights['white_queenside'] and self.is_empty(7, 3) and self.is_empty(7, 2) and self.is_empty(7, 1):
                    if not self.is_square_attacked(7, 3, 'black') and not self.is_square_attacked(7, 2, 'black'):
                        moves.append((7, 2))
            elif color == 'black' and row == 0 and col == 4:
                if self.castling_rights['black_kingside'] and self.is_empty(0, 5) and self.is_empty(0, 6):
                    if not self.is_square_attacked(0, 5, 'white') and not self.is_square_attacked(0, 6, 'white'):
                        moves.append((0, 6))
                if self.castling_rights['black_queenside'] and self.is_empty(0, 3) and self.is_empty(0, 2) and self.is_empty(0, 1):
                    if not self.is_square_attacked(0, 3, 'white') and not self.is_square_attacked(0, 2, 'white'):
                        moves.append((0, 2))
        
        return moves

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece_at(row, col)
                if piece and piece[0] == color and piece[1] == 'K':
                    return (row, col)
        return None

    def is_square_attacked(self, row, col, by_color):
        for r in range(8):
            for c in range(8):
                piece = self.get_piece_at(r, c)
                if piece and piece[0] == by_color:
                    if (r, c) != (row, col):
                        moves = self.get_piece_moves_without_check(r, c, piece[1])
                        if (row, col) in moves:
                            return True
        return False

    def get_piece_moves_without_check(self, row, col, piece_type):
        piece = (self.turn if self.board[row][col][0] == self.turn else 'white', piece_type)
        color = piece[0]
        moves = []
        
        if piece_type == 'P':
            direction = -1 if color == 'white' else 1
            new_row = row + direction
            if 0 <= new_row < 8:
                if self.is_empty(new_row, col):
                    moves.append((new_row, col))
                if 0 <= col - 1 < 8 and self.is_enemy_piece(new_row, col - 1, color):
                    moves.append((new_row, col - 1))
                if 0 <= col + 1 < 8 and self.is_enemy_piece(new_row, col + 1, color):
                    moves.append((new_row, col + 1))
        elif piece_type == 'R':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    if self.is_empty(new_row, new_col):
                        moves.append((new_row, new_col))
                    elif self.is_enemy_piece(new_row, new_col, color):
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        elif piece_type == 'N':
            offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in offsets:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if not self.is_own_piece(new_row, new_col, color):
                        moves.append((new_row, new_col))
        elif piece_type == 'B':
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    if self.is_empty(new_row, new_col):
                        moves.append((new_row, new_col))
                    elif self.is_enemy_piece(new_row, new_col, color):
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        elif piece_type == 'Q':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 8):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    if self.is_empty(new_row, new_col):
                        moves.append((new_row, new_col))
                    elif self.is_enemy_piece(new_row, new_col, color):
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
        elif piece_type == 'K':
            offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in offsets:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if not self.is_own_piece(new_row, new_col, color):
                        moves.append((new_row, new_col))
        
        return moves

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return True
        row, col = king_pos
        enemy_color = 'black' if color == 'white' else 'white'
        return self.is_square_attacked(row, col, enemy_color)

    def does_not_leave_king_in_check(self, from_row, from_col, to_row, to_col, color):
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        in_check = self.is_in_check(color)
        
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        
        return not in_check

    def has_legal_moves(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece_at(row, col)
                if piece and piece[0] == color:
                    if self.get_valid_moves(row, col):
                        return True
        return False

    def execute_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        color, piece_type = piece
        captured_piece = self.board[to_row][to_col]
        
        if captured_piece:
            if captured_piece[0] == 'white':
                self.captured_white.append(captured_piece[1])
            else:
                self.captured_black.append(captured_piece[1])
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        if piece_type == 'P':
            if color == 'white' and to_row == 0:
                self.board[to_row][to_col] = (color, 'Q')
            elif color == 'black' and to_row == 7:
                self.board[to_row][to_col] = (color, 'Q')
            
            if self.en_passant_target and to_row == self.en_passant_target[0] and to_col == self.en_passant_target[1]:
                ep_row = to_row + (1 if color == 'white' else -1)
                captured = self.board[ep_row][to_col]
                if captured:
                    if captured[0] == 'white':
                        self.captured_white.append(captured[1])
                    else:
                        self.captured_black.append(captured[1])
                self.board[ep_row][to_col] = None
            
            if abs(to_row - from_row) == 2:
                self.en_passant_target = ((from_row + to_row) // 2, from_col)
            else:
                self.en_passant_target = None
        else:
            self.en_passant_target = None
        
        if piece_type == 'K':
            if color == 'white':
                self.white_king_moved = True
                if from_col == 4 and to_col == 6:
                    self.board[7][5] = self.board[7][7]
                    self.board[7][7] = None
                elif from_col == 4 and to_col == 2:
                    self.board[7][3] = self.board[7][0]
                    self.board[7][0] = None
            else:
                self.black_king_moved = True
                if from_col == 4 and to_col == 6:
                    self.board[0][5] = self.board[0][7]
                    self.board[0][7] = None
                elif from_col == 4 and to_col == 2:
                    self.board[0][3] = self.board[0][0]
                    self.board[0][0] = None
        
        if piece_type == 'R':
            if color == 'white':
                if from_row == 7 and from_col == 0:
                    self.white_rooks_moved['queenside'] = True
                elif from_row == 7 and from_col == 7:
                    self.white_rooks_moved['kingside'] = True
            else:
                if from_row == 0 and from_col == 0:
                    self.black_rooks_moved['queenside'] = True
                elif from_row == 0 and from_col == 7:
                    self.black_rooks_moved['kingside'] = True
        
        if color == 'white':
            if self.white_king_moved:
                self.castling_rights['white_kingside'] = False
                self.castling_rights['white_queenside'] = False
        else:
            if self.black_king_moved:
                self.castling_rights['black_kingside'] = False
                self.castling_rights['black_queenside'] = False
        
        if color == 'white':
            self.castling_rights['white_kingside'] = False
            if to_row == 7 and to_col == 7:
                self.castling_rights['white_kingside'] = False
            if to_row == 7 and to_col == 0:
                self.castling_rights['white_queenside'] = False
        else:
            if to_row == 0 and to_col == 7:
                self.castling_rights['black_kingside'] = False
            if to_row == 0 and to_col == 0:
                self.castling_rights['black_queenside'] = False

    def check_game_over(self):
        if not self.has_legal_moves(self.turn):
            if self.is_in_check(self.turn):
                self.game_over = True
                self.winner = 'Black' if self.turn == 'white' else 'White'
            else:
                self.game_over = True
                self.winner = 'Draw'
        
        if self.is_insufficient_material():
            self.game_over = True
            self.winner = 'Draw'

    def is_insufficient_material(self):
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece_at(row, col)
                if piece:
                    pieces.append((piece[0], piece[1]))
        
        white_pieces = [p for p in pieces if p[0] == 'white']
        black_pieces = [p for p in pieces if p[0] == 'black']
        
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True
        
        if len(white_pieces) == 1 and white_pieces[0][1] in ['B', 'N'] and len(black_pieces) == 1:
            return True
        
        if len(black_pieces) == 1 and black_pieces[0][1] in ['B', 'N'] and len(white_pieces) == 1:
            return True
        
        return False

    def handle_click(self, pos):
        if self.game_over:
            return
        
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        
        if self.selected_square:
            from_row, from_col = self.selected_square
            if (row, col) in self.valid_moves:
                self.execute_move(from_row, from_col, row, col)
                self.selected_square = None
                self.valid_moves = []
                self.turn = 'black' if self.turn == 'white' else 'white'
                self.check_game_over()
            else:
                piece = self.get_piece_at(row, col)
                if piece and piece[0] == self.turn:
                    self.selected_square = (row, col)
                    self.valid_moves = self.get_valid_moves(row, col)
                else:
                    self.selected_square = None
                    self.valid_moves = []
        else:
            piece = self.get_piece_at(row, col)
            if piece and piece[0] == self.turn:
                self.selected_square = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)

    def update_timer(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_update
        self.last_update = current_time
        
        if not self.game_over:
            if self.turn == 'white':
                self.white_time += elapsed
            else:
                self.black_time += elapsed

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
            
            self.update_timer()
            
            self.draw_board()
            self.draw_info_panel()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()