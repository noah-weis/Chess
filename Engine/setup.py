import logging as log
from Engine.constants import key
from Engine.move_assignment import assign_moves
from Engine.pieces import Pawn, Rook, Knight, Bishop, Queen, King, Piece

def setup_board(board, fen):
    # Clear previous pieces
    board.white_pieces.clear()
    board.black_pieces.clear()
    board.white_king = None
    board.black_king = None
    
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
            square = board.get_square((file, rank))
            if char.isdigit():
                for _ in range(int(char)):
                    square.occupying_piece = None
                    file += 1
            else:
                color = 'white' if char.isupper() else 'black'
                type_name = key[char.upper()]
                square.occupying_piece = create_piece((file, rank), color, type_name)
                board.pieces.append(square.occupying_piece)
                if color == 'white':
                    board.white_pieces.append(square.occupying_piece)
                    if type_name == "king":
                        board.white_king = square.occupying_piece
                    if type_name == "rook":
                        if square.pos == (0, 7):
                            board.white_queenside_rook = square.occupying_piece
                        elif square.pos == (7, 7):
                            board.white_kingside_rook = square.occupying_piece
                else:
                    board.black_pieces.append(square.occupying_piece)
                    if type_name == "king":
                        board.black_king = square.occupying_piece
                    if type_name == "rook":
                        if square.pos == (0, 0):
                            board.black_queenside_rook = square.occupying_piece
                        elif square.pos == (7, 0):
                            board.black_kingside_rook = square.occupying_piece
                file += 1

    board.turn = "white" if active_color == 'w' else 'black'
    board.halfmove_clock = int(halfmove_clock)
    board.fullmove_number = int(fullmove_number)
    board.en_passant_square = None if en_passant_fen == '-' else en_passant_fen

    # Handle en passant square
    if board.en_passant_square:
        file_val = ord(board.en_passant_square[0]) - ord('a')
        ep_row = 8 - int(board.en_passant_square[1])
        last_move_color = "black" if board.turn == "white" else "white"
        if last_move_color == "black":
            pawn_start = (file_val, ep_row - 2)
            pawn_final = (file_val-1, ep_row)
        else:
            pawn_start = (file_val, ep_row + 2)
            pawn_final = (file_val-1, ep_row)
        pawn = board.get_piece(pawn_final)
        log.debug(pawn_final)
        if pawn and pawn.type == "pawn":
            fake_move = {
                "piece": pawn,
                "start": pawn_start,
                "end": pawn_final,
                "captured": None,
            }
            board.moves.append(fake_move)
    
    # Set castling rights
    if 'K' in castling_fen:
        board.white_king.moved = False
        board.white_kingside_rook.moved = False
    if 'Q' in castling_fen:
        board.white_king.moved = False
        board.white_queenside_rook.moved = False
    if 'k' in castling_fen:
        board.black_king.moved = False
        board.black_kingside_rook.moved = False
    if 'q' in castling_fen:
        board.black_king.moved = False
        board.black_queenside_rook.moved = False

    # Assign moves for the current turn.
    assign_moves(board, board.turn)

def create_piece(pos: tuple, color: str, type: str):
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