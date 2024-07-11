"""Board.py"""
import pygame
from typing import List
from Pieces import Pawn, Rook, Knight, Bishop, Queen, King, Piece

key = {
    'P': "pawn",
    'R': "rook",
    'N': "knight",
    'B': "bishop",
    'Q': "queen",
    'K': "king"
}

backwards_key = {
    "pawn": 'P',
    "rook": 'R',
    "knight": 'N',
    "bishop": 'B',
    "queen": 'Q',
    "king": 'K'
}

# Tile creator
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
        # Get the formal notation of the tile
        columns = 'abcdefgh'
        return columns[self.x] + str(8 - self.y)

    def draw(self, display):
        # Draw the tile with the appropriate color and piece icon
        if self.highlight:
            pygame.draw.rect(display, self.highlight_color, self.rect)
        else:
            pygame.draw.rect(display, self.draw_color, self.rect)

        if self.occupying_piece is not None:
            centering_rect = self.occupying_piece.img.get_rect()
            centering_rect.center = self.rect.center
            self.occupying_piece.img = pygame.transform.smoothscale(self.occupying_piece.img, (self.width, self.height))
            display.blit(self.occupying_piece.img, centering_rect.topleft)

# Default configuration

DEFAULT_CONFIG = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Game state checker
class Board:
    def __init__(self, width, height, config=DEFAULT_CONFIG):
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None
        self.turn = 'white'
        self.config = config
        self.white_king = None
        self.black_king = None
        self.white_queenside_rook = None
        self.white_kingside_rook = None
        self.black_queenside_rook = None
        self.black_kingside_rook = None
        self.white_pieces = []
        self.black_pieces = []
        self.halfmove_clock = None
        self.fullmove_number = None
        self.en_passant_square = None
        self.squares = self.generate_squares()
        self.highlighted = []
        self.setup_board(self.config)

    def generate_squares(self):
        # Generate the squares for the board
        output = []
        for y in range(8):
            for x in range(8):
                output.append(Square(x, y, self.tile_width, self.tile_height))
        return output
    
    def setup_board(self, fen):
        # Clear previous pieces
        self.white_pieces.clear()
        self.black_pieces.clear()
        self.white_king = None
        self.black_king = None

        # Parse FEN string
        parsed_fen = fen.split()
        board_fen = parsed_fen[0]
        active_color = parsed_fen[1]
        castling_fen = parsed_fen[2]
        en_passant_fen = parsed_fen[3]
        halfmove_clock = parsed_fen[4]
        fullmove_number = parsed_fen[5]
        rows = board_fen.split('/')
        
        for i, row in enumerate(rows):
            rank = i  # Adjusted for white pieces starting at rank 0
            file = 0
            for char in row:
                square = self.get_square((file, rank))
                if char.isdigit():
                    for _ in range(int(char)):
                        square.occupying_piece = None
                        file += 1
                        square = self.get_square((file, rank))
                else:
                    color = 'white' if char.isupper() else 'black'
                    type_name = key[char.upper()]
                    square.occupying_piece = create_piece((file, rank), color, type_name)
                    
                    if color == 'white':
                        self.white_pieces.append(square.occupying_piece)
                        if type_name == "king":
                            self.white_king = square.occupying_piece
                        if type_name == "rook":
                            if square.pos == (0, 7):
                                self.white_queenside_rook = square.occupying_piece
                            elif square.pos == (7, 7):
                                self.white_kingside_rook = square.occupying_piece
                    else:
                        self.black_pieces.append(square.occupying_piece)
                        if type_name == "king":
                            self.black_king = square.occupying_piece
                        if type_name == "rook":
                            if square.pos == (0, 0):
                                self.black_queenside_rook = square.occupying_piece
                            elif square.pos == (7, 0):
                                self.black_kingside_rook = square.occupying_piece
                    
                    file += 1
        
        self.turn = "white" if active_color == 'w' else 'black'
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)
        if en_passant_fen == '-':
            self.en_passant_square = None
        else:
            self.en_passant_square = en_passant_fen
        
        # Update castling rights
        if 'K' in castling_fen:
            self.white_king.moved = False
            self.white_kingside_rook.moved = False
        if 'Q' in castling_fen:
            self.white_king.moved = False
            self.white_queenside_rook.moved = False
        if 'k' in castling_fen:
            self.black_king.moved = False
            self.black_kingside_rook.moved = False
        if 'q' in castling_fen:
            self.black_king.moved = False
            self.black_queenside_rook.moved = False
    
    def developer_debug(self):
        # Developer debug function
        if self.selected_piece:
            print(self.selected_piece.get_valid_moves(self))
        print(f'white_check: {self._is_in_check("white")} black_check: {self._is_in_check("black")}')
        print(f'white_king: {self.white_king.pos} black_king: {self.black_king.pos}')
        print(self.generate_fen())
    
    def handle_click(self, mx, my):
        x = mx // self.tile_width
        y = my // self.tile_height 
        print(f"Clicked coordinates: ({mx}, {my}) -> Board coordinates: ({x}, {y}) ({self.get_square((x, y)).coord})")

        clicked_square = self.get_square((x, y))
        if clicked_square.occupying_piece:
            print(f"Clicked piece: {clicked_square.occupying_piece.color} {clicked_square.occupying_piece.type}")

        if self.selected_piece is None:
            if clicked_square.occupying_piece is not None:
                if clicked_square.occupying_piece.color == self.turn:
                    self.select_piece(clicked_square)
        elif self.selected_piece.can_move(self, clicked_square.pos):
            save = self.save_state()
            self.selected_piece.move(self, clicked_square.pos)
            if self._is_in_check(self.turn):
                self.restore_state(save)
                self.deselect_piece()
                print("Invalid move: King is in check.")
                return False
            self.deselect_piece(False)
            self.turn = 'white' if self.turn == 'black' else 'black'
            self.fullmove_number += 1
            print("Piece moved successfully.")
        elif clicked_square.occupying_piece is self.selected_piece:
            self.deselect_piece()
        elif clicked_square.occupying_piece is not None:
            self.deselect_piece()
            if clicked_square.occupying_piece.color == self.turn:
                self.select_piece(clicked_square)
        print(f"Current turn: {self.turn}")
        return True
    
    def deselect_piece(self, message=True):
        self.selected_piece = None
        self.unhighlight()
        if message: print("Deselected piece.")
    
    def select_piece(self, clicked_square: Square):
        self.selected_piece = clicked_square.occupying_piece
        self.highlighted = self.selected_piece.get_valid_moves(self)
        self.highlighted.append(self.selected_piece.pos)
        print(f"Selected piece: {self.selected_piece} at position {self.selected_piece.pos}")

    def unhighlight(self):
        for square in self.highlighted:
            self.get_square(square).highlight = False
        self.highlighted = []

    def in_check(self, color, move: List[tuple] = None, save_state=None):
        """
        Check if the given color is in check. Optionally simulate a move before checking.
        """

        if move and save_state:
            self.get_piece(move[0]).move(self, move[1], real_move=False)
            check = self._is_in_check(color)
            self.restore_state(save_state)
            return check
        else:
            return self._is_in_check(color)
    
    def generate_fen(self):
        def get_piece_fen(piece):
            if piece.color == 'white':
                return backwards_key[piece.type]
            else:
                return backwards_key[piece.type].lower()
        
        rows = []
        for rank in range(8):
            empty_squares = 0
            row = []
            for file in range(8):
                square = self.get_square((file, rank))
                if square.occupying_piece:
                    if empty_squares > 0:
                        row.append(str(empty_squares))
                        empty_squares = 0
                    row.append(get_piece_fen(square.occupying_piece))
                else:
                    empty_squares += 1
            if empty_squares > 0:
                row.append(str(empty_squares))
            rows.append(''.join(row))
        
        # Combine rows with '/'
        board_fen = '/'.join(rows)
        
        # Active color
        active_color = 'w' if self.turn == 'white' else 'b'
        
        # Castling availability
        castling_rights = []
        if self.white_king.moved and self.white_kingside_rook.moved:
            castling_rights.append('K')
        if self.white_king.moved and self.white_queenside_rook.moved:
            castling_rights.append('Q')
        if self.black_king.moved and self.black_queenside_rook.moved:
            castling_rights.append('k')
        if self.black_king.moved and self.black_kingside_rook.moved:
            castling_rights.append('q')
        castling_fen = ''.join(castling_rights) if castling_rights else '-'
        
        # En passant target square
        if self.en_passant_square:
            en_passant_fen = self.en_passant_square
        else:
            en_passant_fen = '-'
        
        # Halfmove clock and fullmove number
        halfmove_clock = self.halfmove_clock
        fullmove_number = self.fullmove_number
        
        # Combine all parts
        fen = f"{board_fen} {active_color} {castling_fen} {en_passant_fen} {halfmove_clock} {fullmove_number}"
        return fen


    def save_state(self):
        """
        Save the current board state including positions of all pieces.
        """
        selected_piece = self.selected_piece
        return {
            "fen": self.generate_fen(),
            "selected_piece": selected_piece
        }
    

    def restore_state(self, state):
        """
        Restore the board state to a previously saved state.
        """
        self.selected_piece = state["selected_piece"]
        self.config = state["fen"]
        self.setup_board(self.config)


    def _is_in_check(self, color):
        """
        Check if the king of the given color is in check.
        """
        king_pos = self.get_king_pos(color)
        opposing_pieces = self.get_opposing_pieces(color)
        return any(king_pos in piece.get_moves(self) for piece in opposing_pieces if piece.status)

    def in_checkmate(self, color):
        # these are just quick tests for efficiency because this function is called a lot
        if not self._is_in_check(color):
            return False
        if color == 'white':
            if self.white_king.get_valid_moves(self) != []:
                return False
        else:
            if self.black_king.get_valid_moves(self) != []:
                return False
        
        # heres the real test for checkmate
        for piece in self.get_allied_pieces(color):
            if piece.status:
                if piece.get_valid_moves(self) != []:
                    return False
        return True

    def get_square(self, pos):
        # Get the square object from the given position
        return self.squares[pos[1] * 8 + pos[0]]
    
    def in_bounds(self, pos):
        # Check if the given position is within the board bounds
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def get_piece(self, pos):
        # Get the occupying piece from the given position
        return self.get_square(pos).occupying_piece

    def get_opposing_pieces(self, color):
        # Get the opposing pieces for the given color
        return self.white_pieces if color == 'black' else self.black_pieces
    
    def get_allied_pieces(self, color):
        # Get the allied pieces for the given color
        return self.black_pieces if color == 'black' else self.white_pieces
    
    def get_king_pos(self, color):
        # Get the position of the king for the given color
        return self.white_king.pos if color == 'white' else self.black_king.pos
    
    def draw(self, display):
        # Draw highlighted squares first
        for pos in self.highlighted:
            self.get_square(pos).highlight = True
        
        # Draw squares
        for square in self.squares:
            square.draw(display)


# Piece factory
def create_piece(pos: tuple, color: str, type: str) -> Piece:
    if type == 'pawn':
        return Pawn(pos, color)
    if type == 'rook':
        return Rook(pos, color)
    if type == 'knight':
        return Knight(pos, color)
    if type == 'bishop':
        return Bishop(pos, color)
    if type == 'queen':
        return Queen(pos, color)
    if type == 'king':
        return King(pos, color)
    return None