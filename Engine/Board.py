import pygame
import logging as log
from Engine.pieces import Pawn, Rook, Knight, Bishop, Queen, King, Piece
from Engine.fen_utils import generate_fen
from Engine.constants import key, DEFAULT_CONFIG
import Engine.setup as setup
from Engine import click_handler
# move_assignment functions are imported where needed.
log.basicConfig(level=log.DEBUG)

class Square:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.abs_x = x * width
        self.abs_y = y * height
        self.abs_pos = (self.abs_x, self.abs_y)
        self.pos = (x, y)
        self.color = 'light' if (x + y) % 2 == 0 else 'dark'
        self.draw_color = (181, 136, 99) if self.color == 'light' else (240, 217, 181)
        self.highlight_color = (230, 205, 0) if self.color == 'light' else (235, 235, 0)
        self.occupying_piece = None
        self.coord = self.get_coord()
        self.highlight = False
        self.rect = pygame.Rect(
            self.abs_x,
            self.abs_y,
            self.width,
            self.height
        )
    
    def is_empty(self):
        return self.occupying_piece is None

    def get_coord(self):
        columns = 'abcdefgh'
        return columns[self.x] + str(8 - self.y)

    def draw(self, display):
        if self.highlight:
            pygame.draw.rect(display, self.highlight_color, self.rect)
        else:
            pygame.draw.rect(display, self.draw_color, self.rect)
        if self.occupying_piece is not None:
            centering_rect = self.occupying_piece.img.get_rect()
            centering_rect.center = self.rect.center
            self.occupying_piece.img = pygame.transform.smoothscale(self.occupying_piece.img, (self.width, self.height))
            display.blit(self.occupying_piece.img, centering_rect.topleft)

class Board:
    def __init__(self, width, height, config=DEFAULT_CONFIG):
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None
        self.turn = 'white'
        self.moves = []
        self.config = config
        self.white_king = None
        self.black_king = None
        self.white_queenside_rook = None
        self.white_kingside_rook = None
        self.black_queenside_rook = None
        self.black_kingside_rook = None
        self.white_pieces = []
        self.black_pieces = []
        self.pieces = []
        self.halfmove_clock = None
        self.fullmove_number = None
        self.en_passant_square = None
        self.squares = self.generate_squares()
        self.highlighted = []
        setup.setup_board(self, self.config)

    def generate_squares(self):
        output = []
        for y in range(8):
            for x in range(8):
                output.append(Square(x, y, self.tile_width, self.tile_height))
        return output
    
    def developer_insight(self):
        board_fen = generate_fen(self).split()[0]
        print(f"FEN: {board_fen}")
        print(f"moves: {self.moves}")
        print(self)
    
    def __str__(self):
        rows = []
        board_fen = generate_fen(self).split()[0]
        for row in board_fen.split('/'):
            expanded_row = ''
            for char in row:
                if char.isdigit():
                    expanded_row += ' ' * (int(char) * 3)
                else:
                    expanded_row += f' {char} '
            rows.append(expanded_row.rstrip().ljust(24))
        horizontal_border = '+---' * 8 + '+'
        board_with_borders = horizontal_border + '\n'
        for row in rows:
            if row.strip() == '':
                row = ' ' * 24
            board_with_borders += '|' + '|'.join(row[i:i+3] for i in range(0, len(row), 3)) + '|\n'
            board_with_borders += horizontal_border + '\n'
        return board_with_borders

    def handle_click(self, mx, my):
        return click_handler.handle_click(self, mx, my)

    def remove_piece(self, piece, keep_pos=False):
        try:
            piece.status = False
            if piece.color == 'white':
                self.white_pieces.remove(piece)
            else:
                self.black_pieces.remove(piece)
            self.pieces.remove(piece)
            self.get_square(piece.pos).occupying_piece = None
            if not keep_pos:
                piece.pos = None
        except:
            print(f"-------------------------------ALERT-------------------------------\n\t\t!!!  LOOK HERE YOU DUMBASS   !!!\nError when removing: {piece}\n-------------------------------ALERT-------------------------------")
            raise ValueError
        return piece

    def add_piece(self, piece, pos):
        piece.status = True
        if piece.color == "white":
            self.white_pieces.append(piece)
        else:
            self.black_pieces.append(piece)
        self.pieces.append(piece)
        piece.pos = pos
        self.get_square(pos).occupying_piece = piece

    def pop_king(self, color):
        return self.remove_piece(self.white_king if color == 'white' else self.black_king, keep_pos=True)
    
    def add_king(self, color):
        king = self.white_king if color == 'white' else self.black_king
        self.add_piece(king, king.pos)

    def deselect_piece(self, message=True):
        return click_handler.deselect_piece(self, message)

    def select_piece(self, clicked_square, message=True):
        return click_handler.select_piece(self, clicked_square, message)

    def unhighlight(self):
        return click_handler.unhighlight(self)
    
    def save_state(self):
        selected_piece = self.selected_piece
        return {
            "fen": generate_fen(self),
            "selected_piece": selected_piece
        }

    def restore_state(self, state):
        self.selected_piece = state["selected_piece"]
        self.config = state["fen"]
        setup.setup_board(self, self.config)

    def in_check(self, color):
        from move_assignment import in_check
        return in_check(self, color)

    def in_checkmate(self, color):
        from move_assignment import in_checkmate
        return in_checkmate(self, color)

    def get_square(self, pos):
        return self.squares[pos[1] * 8 + pos[0]]
    
    def in_bounds(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def get_piece(self, pos):
        return self.get_square(pos).occupying_piece

    def get_opposing_pieces(self, color):
        return self.white_pieces if color == 'black' else self.black_pieces
    
    def get_allied_pieces(self, color):
        return self.black_pieces if color == 'black' else self.white_pieces
    
    def get_king_pos(self, color):
        return self.white_king.pos if color == 'white' else self.black_king.pos

    def draw(self, display):
        for pos in self.highlighted:
            self.get_square(pos).highlight = True
        for square in self.squares:
            square.draw(display)
