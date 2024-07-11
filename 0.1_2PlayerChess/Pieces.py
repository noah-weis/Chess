"""Pieces.py"""
import pygame
from typing import List
import Board
import os

# Piece class
class Piece:
    def __init__(self, pos: tuple, color: str, type: str, value: int):
        self.pos = pos
        self.color = color
        self.type = type
        self.value = value
        self.status = True
        image_path = os.path.join('assets', f'{color}_{type}.png')
        try:
            self.img = pygame.image.load(image_path)
        except FileNotFoundError:
            print(f"Image file not found: {image_path}")
            self.img = None 

    def get_value(self):
        return self.value
    
    def move(self, board: Board, new_pos: tuple, real_move=True):
        captured_piece = board.get_piece(new_pos)
        board.get_square(((self.pos))).occupying_piece = None 
        board.get_square(((new_pos))).occupying_piece = self
        self.pos = new_pos
        if captured_piece:
            captured_piece.status = False
        return captured_piece

    def can_move(self, board: Board, new_pos: tuple):
        return new_pos in board.highlighted and new_pos != self.pos
    
    def get_valid_moves(self, board) -> List[tuple]:
        original_pos = self.pos
        valid_moves = []
        potential_moves = self.get_moves(board)

        for move in potential_moves:
            captured_piece = self.move(board, move, real_move=False)
            if not board._is_in_check(self.color):
                valid_moves.append(move)
            self.revert_move(board, original_pos, move, captured_piece)
        return valid_moves

    def revert_move(self, board, original_pos, new_pos, captured_piece):
        board.get_square(((new_pos))).occupying_piece = captured_piece
        board.get_square(((original_pos))).occupying_piece = self
        self.pos = original_pos
        if captured_piece:
            captured_piece.pos = new_pos
            captured_piece.status = True
    

class Pawn(Piece):
    def __init__(self, pos: tuple, color: str):
        super().__init__(pos, color, "pawn", 1)
        self.moved = False
        self.direction = -1 if color == 'white' else 1

    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        
        # move forward
        if board.in_bounds((x, y + self.direction)) and board.get_square((x, y + self.direction)).is_empty():
            moves.append((x, y + self.direction))
            # move two squares forward (if not moved yet)
            if not self.moved and board.in_bounds((x, y + 2 * self.direction)) and board.get_square((x, y + 2 * self.direction)).is_empty():
                moves.append((x, y + 2 * self.direction))
        
        # Capture moves
        for dx in [-1, 1]:
            nx, ny = x + dx, y + self.direction
            if board.in_bounds((nx, ny)) and not board.get_square((nx, ny)).is_empty():
                if board.get_piece((nx, ny)).color != self.color:
                    moves.append((nx, ny))
        
        # TODO: En passant
        
        return moves
    
    def move(self, board: Board, new_pos: tuple, real_move=True):
        if real_move:
            self.moved = True
        return super().move(board, new_pos)
        
class Rook(Piece):
    def __init__(self, pos: tuple, color: str, moved=True):
        super().__init__(pos, color, "rook", 5)
        self.moved = moved
    
    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        
        # horizontal moves
        for i in range(x + 1, 8):
            if board.get_square((i, y)).is_empty():
                moves.append((i, y))
            else:
                if board.get_piece(((i, y))).color != self.color:
                    moves.append((i, y))
                break
        
        for i in range(x - 1, -1, -1):
            if board.get_square((i, y)).is_empty():
                moves.append((i, y))
            else:
                if board.get_piece(((i, y))).color != self.color:
                    moves.append((i, y))
                break
        
        # vertical moves
        for i in range(y + 1, 8):
            if board.get_square((x, i)).is_empty():
                moves.append((x, i))
            else:
                if board.get_piece(((x, i))).color != self.color:
                    moves.append((x, i))
                break
        
        for i in range(y - 1, -1, -1):
            if board.get_square((x, i)).is_empty():
                moves.append((x, i))
            else:
                if board.get_piece(((x, i))).color != self.color:
                    moves.append((x, i))
                break
        
        return moves
    
    def move(self, board: Board, new_pos: tuple, real_move=True):
        if real_move:
            self.moved = True
        return super().move(board, new_pos)
        

class Knight(Piece):
    def __init__(self, pos: tuple, color: str):
        super().__init__(pos, color, "knight", 3)
    
    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        
        for dx, dy in [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if board.get_piece((new_x, new_y)) == None or board.get_piece((new_x, new_y)).color != self.color:
                    moves.append((new_x, new_y))
        
        return moves
    


class Bishop(Piece):
    def __init__(self, pos: tuple, color: str):
        super().__init__(pos, color, "bishop", 3)
    
    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        
        # diagonal moves
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if board.get_square((new_x, new_y)).is_empty():
                    moves.append((new_x, new_y))
                else:
                    if board.get_piece(((new_x, new_y))).color != self.color:
                        moves.append((new_x, new_y))
                    break
                new_x += dx
                new_y += dy
        
        return moves

class Queen(Piece):
    def __init__(self, pos: tuple, color: str):
        super().__init__(pos, color, "queen", 9)
    
    def get_moves(self, board: Board) -> List[tuple]:
        """
        Basically a mashup of the Rook and Bishop get_moves methods
        """
        x, y = self.pos
        moves = []
        
        # horizontal moves
        for i in range(x + 1, 8):
            if board.get_square((i, y)).is_empty():
                moves.append((i, y))
            else:
                if board.get_piece((i, y)).color != self.color:
                    moves.append((i, y))
                break
        
        for i in range(x - 1, -1, -1):
            if board.get_square((i, y)).is_empty():
                moves.append((i, y))
            else:
                if board.get_piece((i, y)).color != self.color:
                    moves.append((i, y))
                break
        
        # vertical moves
        for i in range(y + 1, 8):
            if board.get_square((x, i)).is_empty():
                moves.append((x, i))
            else:
                if board.get_piece((x, i)).color != self.color:
                    moves.append((x, i))
                break
        
        for i in range(y - 1, -1, -1):
            if board.get_square((x, i)).is_empty():
                moves.append((x, i))
            else:
                if board.get_piece((x, i)).color != self.color:
                    moves.append((x, i))
                break
        
        # diagonal moves
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < 8 and 0 <= new_y < 8:
                if board.get_square((new_x, new_y)).is_empty():
                    moves.append((new_x, new_y))
                else:
                    if board.get_piece((new_x, new_y)).color != self.color:
                        moves.append((new_x, new_y))
                    break
                new_x += dx
                new_y += dy
        
        return moves

class King(Piece):
    def __init__(self, pos: tuple, color: str, moved=True):
        super().__init__(pos, color, "king", 100)
        self.moved = moved
    
    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 8 and 0 <= new_y < 8:
                    if board.get_square((new_x, new_y)).is_empty() or board.get_piece((new_x, new_y)).color != self.color:
                        moves.append((new_x, new_y))
        
        # Castling
        if not self.moved:
            # King side
            if board.get_piece((7, y))and board.get_piece((7, y)).type == "rook" and not board.get_piece((7, y)).moved and board.get_square((5, y)).is_empty() and board.get_square((6, y)).is_empty() and board.get_piece((7, y)).color == self.color:
                moves.append((6, y))

            # Queen side
            if board.get_piece((0, y))and board.get_piece((0, y)).type == "rook" and not board.get_piece((0, y)).moved and board.get_square((1, y)).is_empty() and board.get_square((2, y)).is_empty() and board.get_square((3, y)).is_empty() and board.get_piece((0, y)).color == self.color:
                moves.append((2, y))

        return moves
    
    def move(self, board: Board, new_pos: tuple, real_move=True):
        # if we are castling, also move the rook
        if abs(new_pos[0] - self.pos[0]) == 2:
            if new_pos[0] == 6:
                board.get_piece((7, new_pos[1])).move(board, (5, new_pos[1]))
            else:
                board.get_piece((0, new_pos[1])).move(board, (3, new_pos[1]))
        if real_move:
            self.moved = True
        return super().move(board, new_pos)
    
    def revert_move(self, board, original_pos, new_pos, captured_piece):
        # if we castled we need to move back the rook as well
        if abs(original_pos[0] - self.pos[0]) == 2:
            if new_pos[0] == 6:
                board.get_piece((5, new_pos[1])).move(board, (7, new_pos[1]))
            else:
                board.get_piece((3, new_pos[1])).move(board, (0, new_pos[1]))
        return super().revert_move(board, original_pos, new_pos, captured_piece)
