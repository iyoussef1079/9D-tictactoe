import unittest
from core.board_9D import Board_9D

class TestBoard9D(unittest.TestCase):
    def test_initial_board_state(self):
        """Test that the initial state of the 9D board is all None."""
        board_9d = Board_9D()
        single_board_expected = [[None for _ in range(3)] for _ in range(3)]
        expected = [[single_board_expected for _ in range(3)] for _ in range(3)]
        actual = board_9d.to_serializable()

        self.assertEqual(actual, expected, "The initial board state should be all None")


    def test_place_piece(self):
        """Test that placing a piece on the 9D board works."""
        board_9d = Board_9D()
        board_9d.place_piece(0, 0, 0, 0, "X")
        expected = [[[[None, None, None], [None, None, None], [None, None, None]] for _ in range(3)] for _ in range(3)]
        expected[0][0][0][0] = "X"
        actual = board_9d.to_serializable()

        self.assertEqual(actual, expected, "Placing a piece on the board should work")