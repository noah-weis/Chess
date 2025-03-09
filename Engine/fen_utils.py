import logging as log
from Engine.constants import key, DEFAULT_CONFIG, backwards_key

def generate_fen(board):
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
            square = board.get_square((file, rank))
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
    
    board_fen = '/'.join(rows)
    active_color = 'w' if board.turn == 'white' else 'b'
    
    # Castling rights (logic preserved from your original code)
    castling_rights = []
    if board.white_king.moved and board.white_kingside_rook.moved:
        castling_rights.append('K')
    if board.white_king.moved and board.white_queenside_rook.moved:
        castling_rights.append('Q')
    if board.black_king.moved and board.black_queenside_rook.moved:
        castling_rights.append('k')
    if board.black_king.moved and board.black_kingside_rook.moved:
        castling_rights.append('q')
    castling_fen = ''.join(castling_rights) if castling_rights else '-'
    
    en_passant_fen = board.en_passant_square if board.en_passant_square else '-'
    halfmove_clock = board.halfmove_clock
    fullmove_number = board.fullmove_number
    fen = f"{board_fen} {active_color} {castling_fen} {en_passant_fen} {halfmove_clock} {fullmove_number}"
    return fen