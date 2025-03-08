"""
This file tests move generation by comparing the expected number of moves/nodes for
given board states. The tests are separated into two classes: one for boards where
depth==1 (non-depth tests) and one for deeper tests.
"""

import Board
import Pieces
import unittest

def draw_board(fen):
    """
    Render a board diagram from the FEN string.
    This function uses only the board portion (the first field) of the FEN.
    """
    board_part = fen.split()[0]
    rows = []
    for row in board_part.split('/'):
        expanded_row = ''
        for char in row:
            if char.isdigit():
                expanded_row += ' ' * (int(char) * 3)  # Three spaces per empty square
            else:
                expanded_row += f' {char} '  # Center the piece in a 3-char-wide space
        rows.append(expanded_row.rstrip().ljust(24))
    horizontal_border = '+---' * 8 + '+'
    board_with_borders = horizontal_border + '\n'
    for row in rows:
        if row.strip() == '':
            row = ' ' * 24
        board_with_borders += '|' + '|'.join(row[i:i+3] for i in range(0, len(row), 3)) + '|\n'
        board_with_borders += horizontal_border + '\n'
    return board_with_borders

# Test positions for both groups
test_positions = [
    {"depth": 1, "nodes": 8, "fen": "r6r/1b2k1bq/8/8/7B/8/8/R3K2R b KQ - 3 2"},
    {"depth": 1, "nodes": 8, "fen": "8/8/8/2k5/2pP4/8/B7/4K3 b - d3 0 3"},
    {"depth": 1, "nodes": 19, "fen": "r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w KQkq - 2 2"},
    {"depth": 1, "nodes": 5, "fen": "r3k2r/p1pp1pb1/bn2Qnp1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQkq - 3 2"},
    {"depth": 1, "nodes": 44, "fen": "2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b KQ - 3 2"},
    {"depth": 1, "nodes": 39, "fen": "rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w KQ - 3 9"},
    {"depth": 1, "nodes": 9, "fen": "2r5/3pk3/8/2P5/8/2K5/8/8 w - - 5 4"},
    {"depth": 3, "nodes": 62379, "fen": "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"},
    {"depth": 3, "nodes": 89890, "fen": "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"},
    {"depth": 6, "nodes": 1134888, "fen": "3k4/3p4/8/K1P4r/8/8/8/8 b - - 0 1"},
    {"depth": 6, "nodes": 1015133, "fen": "8/8/4k3/8/2p5/8/B2P2K1/8 w - - 0 1"},
    {"depth": 6, "nodes": 1440467, "fen": "8/8/1k6/2b5/2pP4/8/5K2/8 b - d3 0 1"},
    {"depth": 6, "nodes": 661072, "fen": "5k2/8/8/8/8/8/8/4K2R w K - 0 1"},
    {"depth": 6, "nodes": 803711, "fen": "3k4/8/8/8/8/8/8/R3K3 w Q - 0 1"},
    {"depth": 4, "nodes": 1274206, "fen": "r3k2r/1b4bq/8/8/8/8/7B/R3K2R w KQkq - 0 1"},
    {"depth": 4, "nodes": 1720476, "fen": "r3k2r/8/3Q4/8/8/5q2/8/R3K2R b KQkq - 0 1"},
    {"depth": 6, "nodes": 3821001, "fen": "2K2r2/4P3/8/8/8/8/8/3k4 w - - 0 1"},
    {"depth": 5, "nodes": 1004658, "fen": "8/8/1P2K3/8/2n5/1q6/8/5k2 b - - 0 1"},
    {"depth": 6, "nodes": 217342, "fen": "4k3/1P6/8/8/8/8/K7/8 w - - 0 1"},
    {"depth": 6, "nodes": 92683, "fen": "8/P1k5/K7/8/8/8/8/8 w - - 0 1"},
    {"depth": 6, "nodes": 2217, "fen": "K1k5/8/P7/8/8/8/8/8 w - - 0 1"},
    {"depth": 7, "nodes": 567584, "fen": "8/k1P5/8/1K6/8/8/8/8 w - - 0 1"},
    {"depth": 4, "nodes": 23527, "fen": "8/8/2k5/5q2/5n2/8/5K2/8 b - - 0 1"}
]

# Split tests into those with depth==1 and those with deeper searches.
depth_one_tests = [pos for pos in test_positions if pos["depth"] == 1]
deeper_tests = [pos for pos in test_positions if pos["depth"] != 1]

###############################################################################
# Tests for positions with depth==1 (non-depth tests)
###############################################################################
class TestMoveGenerationDepthOne(unittest.TestCase):
    def _run_board_test(self, fen, expected_nodes):
        board = Board.Board(600, 600, config=fen)
        board.assign_moves(board.turn)
        total_moves = sum(
            len(piece.legal_moves) for piece in board.pieces if piece.color == board.turn
        )
        error_msg = (
            f"Failed for board:\n{draw_board(fen)}\n"
            f"Expected {expected_nodes} moves, got {total_moves}"
        )
        self.assertEqual(total_moves, expected_nodes, error_msg)
    
    def test_board_0(self):
        pos = depth_one_tests[0]
        self._run_board_test(pos["fen"], pos["nodes"])
    
    def test_board_1(self):
        pos = depth_one_tests[1]
        self._run_board_test(pos["fen"], pos["nodes"])
    
    def test_board_2(self):
        pos = depth_one_tests[2]
        self._run_board_test(pos["fen"], pos["nodes"])
    
    def test_board_3(self):
        pos = depth_one_tests[3]
        self._run_board_test(pos["fen"], pos["nodes"])
    
    def test_board_4(self):
        pos = depth_one_tests[4]
        self._run_board_test(pos["fen"], pos["nodes"])
    
    def test_board_5(self):
        pos = depth_one_tests[5]
        self._run_board_test(pos["fen"], pos["nodes"])
    
    def test_board_6(self):
        pos = depth_one_tests[6]
        self._run_board_test(pos["fen"], pos["nodes"])

###############################################################################
# Tests for positions with depth > 1 (deeper tests)
###############################################################################
@unittest.skip("Depth tests are not set up yet")
class TestMoveGenerationDeeper(unittest.TestCase):
    def _run_board_test(self, fen, expected_nodes, depth):
        board = Board.Board(600, 600, config=fen)
        # Assume board.perft(depth) returns the total node count at the given depth.
        total_nodes = board.perft(depth)
        error_msg = (
            f"Failed for board:\n{draw_board(fen)}\n"
            f"Depth: {depth}\nExpected {expected_nodes} nodes, got {total_nodes}"
        )
        self.assertEqual(total_nodes, expected_nodes, error_msg)
    
    def test_board_7(self):
        pos = deeper_tests[0]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_8(self):
        pos = deeper_tests[1]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_9(self):
        pos = deeper_tests[2]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_10(self):
        pos = deeper_tests[3]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_11(self):
        pos = deeper_tests[4]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_12(self):
        pos = deeper_tests[5]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_13(self):
        pos = deeper_tests[6]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_14(self):
        pos = deeper_tests[7]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_15(self):
        pos = deeper_tests[8]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_16(self):
        pos = deeper_tests[9]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_17(self):
        pos = deeper_tests[10]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_18(self):
        pos = deeper_tests[11]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_19(self):
        pos = deeper_tests[12]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_20(self):
        pos = deeper_tests[13]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_21(self):
        pos = deeper_tests[14]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])
    
    def test_board_22(self):
        pos = deeper_tests[15]
        self._run_board_test(pos["fen"], pos["nodes"], pos["depth"])

if __name__ == "__main__":
    unittest.main()
