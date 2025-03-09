from Engine.move_assignment import assign_moves, in_checkmate
"""
click_handler.py
"""

def handle_click(board, mx, my):
    x = mx // board.tile_width
    y = my // board.tile_height
    print(f"Clicked coordinates: ({mx}, {my}) -> Board coordinates: ({x}, {y}) ({board.get_square((x, y)).coord})")
    clicked_square = board.get_square((x, y))
    print(f"Clicked piece: {clicked_square.occupying_piece}")
    
    if board.selected_piece is None:
        if clicked_square.occupying_piece is not None:
            if clicked_square.occupying_piece.color == board.turn:
                select_piece(board, clicked_square)
    elif board.selected_piece.can_move(board, clicked_square.pos):
        move_piece(board, clicked_square)
        checkmate = board.turn if in_checkmate(board, board.turn) else False
        if checkmate:
            return 'White' if checkmate == 'black' else 'Black'
    elif clicked_square.occupying_piece is board.selected_piece:
        deselect_piece(board)
    elif clicked_square.occupying_piece is not None:
        deselect_piece(board)
        if clicked_square.occupying_piece.color == board.turn:
            select_piece(board, clicked_square)
    print(f"Current turn: {board.turn}\n----------------------")

def move_piece(board, clicked_square):
    move = generate_move(board, board.selected_piece, clicked_square.pos)
    board.moves.append(move)
    captured = board.selected_piece.move(board, clicked_square.pos)
    if captured:
        print(f"{captured} at {clicked_square.pos} has been captured by {board.selected_piece}.")
    board.turn = 'white' if board.turn == 'black' else 'black'
    board.fullmove_number += 1
    deselect_piece(board)
    assign_moves(board, board.turn)
    print("Piece moved.")

def generate_move(board, piece, new_pos):
    move = {
        "piece": piece,
        "start": piece.pos,
        "end": new_pos,
        "captured": board.get_piece(new_pos),
    }
    return move

def deselect_piece(board, message=True):
    board.selected_piece = None
    unhighlight(board)
    if message: print("Deselected piece.")

def select_piece(board, clicked_square, message=True):
    board.selected_piece = clicked_square.occupying_piece
    board.highlighted = board.selected_piece.legal_moves.copy()
    board.highlighted.append(board.selected_piece.pos)
    if message: print(f"Selected piece: {board.selected_piece} at position {board.selected_piece.pos}\nLegal moves: {board.selected_piece.legal_moves}")

def unhighlight(board):
    for pos in board.highlighted:
        board.get_square(pos).highlight = False
    board.highlighted = []
