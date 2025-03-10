"""Pieces.py"""
import pygame
from typing import List
import Engine.board as Board
import os

# Piece class
class Piece:
    def __init__(self, pos: tuple, color: str, type: str, value: int):
        self.pos = pos
        self.color = color
        self.type = type
        self.value = value
        self.status = True
        self.psudo_legal_moves = []
        self.legal_moves = []
        image_path = os.path.join('assets', f'{color}_{type}.png')
        try:
            self.img = pygame.image.load(image_path)
        except FileNotFoundError:
            print(f"Image file not found: {image_path}")
            self.img = None 
        if not self.img:
            raise ValueError(f"Invalid image path: {image_path}")

    def get_value(self):
        return self.value
    
    def move(self, board: Board, new_pos: tuple, real_move=True):
        captured_piece = board.get_piece(new_pos)
        if captured_piece:
            board.remove_piece(captured_piece)
        board.get_square(new_pos).occupying_piece = self
        board.get_square(self.pos).occupying_piece = None
        self.pos = new_pos
        return captured_piece

    def can_move(self, board: Board, new_pos: tuple):
        return new_pos in board.highlighted and new_pos != self.pos

    def revert_move(self, board, original_pos, new_pos, captured_piece):
        board.get_piece(new_pos).move(board, original_pos, real_move=False)
        if captured_piece:
            board.add_piece(captured_piece, new_pos)
            
    def __repr__(self) -> str:
        return f"{self.color} {self.type} at {self.pos}"
    
    def __str__(self) -> str:
        return repr(self)
    

class Pawn(Piece):
    def __init__(self, pos: tuple, color: str):
        super().__init__(pos, color, "pawn", 1)
        self.moved = False
        self.direction = -1 if color == 'white' else 1

    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        king = board.pop_king("white" if self.color == "black" else "black")
        
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
        
        # En passant
        if len(board.moves) > 0:
            last_move = board.moves[-1]
            if last_move["piece"].type == "pawn" and abs(last_move["start"][1] - last_move["end"][1]) == 2 and last_move["end"][0] == x + 1 and last_move["end"][1] == y:
                moves.append((x + 1, y + self.direction))
            elif last_move["piece"].type == "pawn" and abs(last_move["start"][1] - last_move["end"][1]) == 2 and last_move["end"][0] == x - 1 and last_move["end"][1] == y:
                moves.append((x - 1, y + self.direction))
        
        self.psudo_legal_moves = moves
        board.add_king("white" if self.color == "black" else "black")
        return moves
    
    def move(self, board: Board, new_pos: tuple, real_move=True):
        # en passant
        if abs(new_pos[0] - self.pos[0]) == 1 and board.get_square(new_pos).is_empty():
            board.get_piece((new_pos[0], new_pos[1] - self.direction)).move(board, new_pos)

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
        king = board.pop_king("white" if self.color == "black" else "black")
        
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
        
        board.add_king("white" if self.color == "black" else "black")
        self.psudo_legal_moves = moves
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
        board.pop_king("white" if self.color == "black" else "black")

        for dx, dy in [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if board.get_piece((new_x, new_y)) == None or board.get_piece((new_x, new_y)).color != self.color:
                    moves.append((new_x, new_y))
        
        board.add_king("white" if self.color == "black" else "black")
        self.psudo_legal_moves = moves
        return moves
    


class Bishop(Piece):
    def __init__(self, pos: tuple, color: str):
        super().__init__(pos, color, "bishop", 3)
    
    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        board.pop_king("white" if self.color == "black" else "black")
        
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
        
        board.add_king("white" if self.color == "black" else "black")
        self.psudo_legal_moves = moves
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
        board.pop_king("white" if self.color == "black" else "black")
        
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
        
        board.add_king("white" if self.color == "black" else "black")
        self.psudo_legal_moves = moves
        return moves

class King(Piece):
    def __init__(self, pos: tuple, color: str, moved=True):
        super().__init__(pos, color, "king", 100)
        self.moved = moved
    
    def get_moves(self, board: Board) -> List[tuple]:
        x, y = self.pos
        moves = []
        board.pop_king("white" if self.color == "black" else "black")
        
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
        
        board.add_king("white" if self.color == "black" else "black")
        self.psudo_legal_moves = moves
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
