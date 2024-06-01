import unittest
from core.board_9D import Board_9D
from core.exceptions import CellOccupiedError

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
        board_9d.place_piece([0, 0], [0, 0], "X")
        expected = [[[[None, None, None], [None, None, None], [None, None, None]] for _ in range(3)] for _ in range(3)]
        expected[0][0][0][0] = "X"
        actual = board_9d.to_serializable()

        self.assertEqual(actual, expected, "Placing a piece on the board should work")


    def test_place_piece_occupied(self):
        board_9d = Board_9D()
        board_9d.place_piece([0, 0], [0, 0], "X")
        with self.assertRaises(CellOccupiedError, msg="Should raise CellOccupiedError when trying to place a piece in an occupied cell"):
            board_9d.place_piece([0, 0], [0, 0], "X")


    def test_board_has_81_cells(self):
        """Test that the 9D board has exactly 81 cells."""
        board_9d = Board_9D()
        actual = board_9d.to_serializable()
        cell_count = sum(sum(len(board_row) for board_row in board) for row in actual for board in row)

        self.assertEqual(cell_count, 81, "The 9D board should have exactly 81 cells")