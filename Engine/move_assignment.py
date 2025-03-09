def find_squares_between(start, end):
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

def clear_moves(board):
    for piece in board.pieces:
        piece.legal_moves = []

def assign_moves(board, color):
    clear_moves(board)
    attacking_pieces = []
    attacked_squares = []
    king_pos = board.get_king_pos(color)
    for piece in board.get_opposing_pieces(color):
        new_attacked_squares = piece.get_moves(board)
        if king_pos in new_attacked_squares:
            attacking_pieces.append(piece)
        attacked_squares += new_attacked_squares
    king = board.white_king if color == 'white' else board.black_king
    king.legal_moves = [move for move in king.get_moves(board) if move not in attacked_squares]
    if len(attacking_pieces) > 1:
        return  # Double check – king must move.
    elif len(attacking_pieces) == 1:
        blocking_squares = find_squares_between(king_pos, attacking_pieces[0].pos)
        for piece in board.get_allied_pieces(color):
            if piece.type == 'king':
                continue
            piece.legal_moves = [move for move in piece.get_moves(board) if move in blocking_squares]
    else:
        for piece in board.get_allied_pieces(color):
            if piece.type == 'king':
                continue
            piece.legal_moves = piece.get_moves(board)

def in_check(board, color):
    king_pos = board.get_king_pos(color)
    opposing_pieces = board.get_opposing_pieces(color)
    return any(king_pos in piece.legal_moves for piece in opposing_pieces if piece.status)

def in_checkmate(board, color):
    if not in_check(board, color):
        return False
    if color == 'white':
        if board.white_king.legal_moves != []:
            return False
    else:
        if board.black_king.legal_moves != []:
            return False
    for piece in board.get_allied_pieces(color):
        if piece.status and piece.legal_moves != []:
            return False
    return True
