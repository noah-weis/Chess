"""Board.py"""
import pygame
from Pieces import Pawn, Rook, Knight, Bishop, Queen, King, Piece
from typing import Tuple, List
import logging as log

log.basicConfig(level=log.DEBUG)

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
                else:
                    color = 'white' if char.isupper() else 'black'
                    type_name = key[char.upper()]
                    square.occupying_piece = create_piece((file, rank), color, type_name)
                    
                    self.pieces.append(square.occupying_piece)
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
        
        # Set game state variables
        self.turn = "white" if active_color == 'w' else 'black'
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)
        if en_passant_fen == '-':
            self.en_passant_square = None
        else:
            self.en_passant_square = en_passant_fen
        
        # en passant square
        if self.en_passant_square:
            # Convert FEN algebraic notation (e.g., "e5") to internal board coordinates.
            file = ord(self.en_passant_square[0]) - ord('a')
            # Use 8 - rank because row 0 corresponds to FEN rank 8.
            ep_row = 8 - int(self.en_passant_square[1])

            # Determine the color that just moved.
            last_move_color = "black" if self.turn == "white" else "white"

            if last_move_color == "black":
                # For a black pawn, a double move from rank 7 to rank 5 becomes from (file, 1) to (file, 3).
                pawn_start = (file, ep_row - 2)  # 3 - 2 = 1
                pawn_final = (file-1, ep_row)        # 3
            else:
                # For a white pawn, a double move from rank 2 to rank 4 becomes from (file, 6) to (file, 4).
                pawn_start = (file, ep_row + 2)
                pawn_final = (file-1, ep_row)

            # Get the pawn that supposedly double-moved.
            pawn = self.get_piece(pawn_final)
            log.debug(pawn_final)
            if pawn and pawn.type == "pawn":
                fake_move = {
                    "piece": pawn,
                    "start": pawn_start,
                    "end": pawn_final,
                    "captured": None,
                }
                self.moves.append(fake_move)

        
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

        self.assign_moves(self.turn)

    def developer_insight(self):
        board_fen = self.generate_fen().split()[0]
        print(f"FEN: {board_fen}")
        print(f"moves: {self.moves}")
        print(self)
    
    def __str__(self):
        # Initialize an empty list to store the rows
        rows = []
        board_fen = self.generate_fen().split()[0]
        # Iterate over each row in the FEN board part
        for row in board_fen.split('/'):
            expanded_row = ''
            for char in row:
                if char.isdigit():
                    expanded_row += ' ' * (int(char) * 3)  # Three spaces for each empty square
                else:
                    expanded_row += f' {char} '  # Center the piece in a 3-character wide space
            # Add the expanded row to the list with padding for the last column
            rows.append(expanded_row.rstrip().ljust(24))  # Ensure even spacing for the last column
        
        # Create the top and bottom border of the board
        horizontal_border = '+---' * 8 + '+'
        
        # Assemble the full board with borders
        board_with_borders = horizontal_border + '\n'
        for row in rows:
            # If the row is completely empty, ensure it's filled with spaces
            if row.strip() == '':
                row = ' ' * 24
            board_with_borders += '|' + '|'.join(row[i:i+3] for i in range(0, len(row), 3)) + '|\n'
            board_with_borders += horizontal_border + '\n'
        
        return board_with_borders
    
    def handle_click(self, mx, my):
        x = mx // self.tile_width
        y = my // self.tile_height 
        print(f"Clicked coordinates: ({mx}, {my}) -> Board coordinates: ({x}, {y}) ({self.get_square((x, y)).coord})")

        clicked_square = self.get_square((x, y))
        print(f"Clicked piece: {clicked_square.occupying_piece}")

        if self.selected_piece is None:
            if clicked_square.occupying_piece is not None:
                if clicked_square.occupying_piece.color == self.turn:
                    self.select_piece(clicked_square)
        elif self.selected_piece.can_move(self, clicked_square.pos):
            self.move_piece(clicked_square)
            # Check for checkmate
            checkmate = self.turn if self.in_checkmate(self.turn) else False
            if checkmate:
                return 'White' if checkmate == 'black' else 'Black'
        elif clicked_square.occupying_piece is self.selected_piece:
            self.deselect_piece()
        elif clicked_square.occupying_piece is not None:
            self.deselect_piece()
            if clicked_square.occupying_piece.color == self.turn:
                self.select_piece(clicked_square)
        print(f"Current turn: {self.turn}\n----------------------")
    
    def move_piece(self, clicked_square):
        self.moves.append(self.generate_move(self.selected_piece, clicked_square.pos))
        captured = self.selected_piece.move(self, clicked_square.pos)
        if captured:
            print(f"{captured} at {clicked_square.pos} has been captured by {self.selected_piece}.")
        self.turn = 'white' if self.turn == 'black' else 'black'
        self.fullmove_number += 1
        self.deselect_piece()
        self.assign_moves(self.turn)
        print("Piece moved.")
    
    def generate_move(self, piece, new_pos):
        move = {
            "piece": piece,
            "start": piece.pos,
            "end": new_pos,
            "captured": self.get_piece(new_pos),
        }
        return move
    
    def find_squares_between(self, start, end):
        # Find the squares between two positions, inclusive
        squares = [start, end]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if dx == 0:
            for i in range(1, abs(dy)):
                squares.append((start[0], start[1] + i * dy // abs(dy)))
        elif dy == 0:
            for i in range(1, abs(dx)):
                squares.append((start[0] + i * dx // abs(dx), start[1]))
        elif abs(dx) == abs(dy):
            for i in range(1, abs(dx)):
                squares.append((start[0] + i * dx // abs(dx), start[1] + i * dy // abs(dy)))
        return squares
    
    def clear_moves(self):
        for piece in self.pieces:
            piece.legal_moves = []

    def assign_moves(self, color):
        self.clear_moves()
        attacking_pieces = []
        attacked_squares = []
        king_pos = self.get_king_pos(color)
        for piece in self.get_opposing_pieces(color):
            new_attacked_squares = piece.get_moves(self)
            if king_pos in new_attacked_squares:
                attacking_pieces.append(piece)
            attacked_squares += new_attacked_squares
        king = self.white_king if color == 'white' else self.black_king
        king.legal_moves = [move for move in king.get_moves(self) if move not in attacked_squares]
        if len(attacking_pieces) > 1:
            return # double check - king has to move, can't block both checks with any 1 piece
        elif len(attacking_pieces) == 1:
            blocking_squares = self.find_squares_between(king_pos, attacking_pieces[0].pos)
            for piece in self.get_allied_pieces(color):
                if piece.type == 'king':
                    continue
                piece.legal_moves = [move for move in piece.get_moves(self) if move in blocking_squares]
        else:
            for piece in self.get_allied_pieces(color):
                if piece.type == 'king':
                    continue
                piece.legal_moves = piece.get_moves(self)
        
    def pop_king(self, color):
        # Get the king for the given color and remove it from the board
        return self.remove_piece(self.white_king if color == 'white' else self.black_king, keep_pos=True)
    
    def add_king(self, color):
        # Add the king for the given color back to the board
        king = self.white_king if color == 'white' else self.black_king
        self.add_piece(king, king.pos)
        
    def remove_piece(self, piece, keep_pos=False):
        # Remove the piece at the given position
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
            print(f"-------------------------------ALERT-------------------------------\n\t\t!!!  LOOK HERE YOU DUMBASS   !!!\nError when removing: {piece}\n-------------------------------ALERT-------------------------------") # this function is my achilles heel... let me be
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

    def deselect_piece(self, message=True):
        self.selected_piece = None
        self.unhighlight()
        if message: print("Deselected piece.")

    def select_piece(self, clicked_square: Square, message=True):
        self.selected_piece = clicked_square.occupying_piece
        self.highlighted = self.selected_piece.legal_moves
        self.highlighted.append(self.selected_piece.pos)
        if message: print(f"Selected piece: {self.selected_piece} at position {self.selected_piece.pos}\nLegal moves: {self.selected_piece.legal_moves}")

    def unhighlight(self):
        for square in self.highlighted:
            self.get_square(square).highlight = False
        self.highlighted = []
    
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


    def in_check(self, color):
        """
        Check if the king of the given color is in check.
        """
        king_pos = self.get_king_pos(color)
        opposing_pieces = self.get_opposing_pieces(color)
        return any(king_pos in piece.legal_moves for piece in opposing_pieces if piece.status)

    def in_checkmate(self, color):
        # these are just quick tests for efficiency because this function is called a lot
        if not self.in_check(color):
            return False
        if color == 'white':
            if self.white_king.legal_moves != []:
                return False
        else:
            if self.black_king.legal_moves != []:
                return False
        
        # heres the real test for checkmate
        for piece in self.get_allied_pieces(color):
            if piece.status:
                if piece.legal_moves != []:
                    return False
        return True

    def get_square(self, pos):
        # Get the square object from the given position
        #log.debug(f"get_square({pos})")
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