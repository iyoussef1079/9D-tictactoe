import unittest
from core.board_9D import Board
from core.game_checker import GameChecker

class TestGameChecker(unittest.TestCase):

    def test_check_winner(self):
        # Test various winning scenarios for 'X' and 'O'
        # Horizontal win for 'X'
        board = Board()
        board.board = [['X', 'X', 'X'], [None, None, None], [None, None, None]]
        self.assertEqual(GameChecker.check_winner(board), 'X', "X should win horizontally on top row")

        # Vertical win for 'O'
        board.board = [[None, 'O', None], [None, 'O', None], [None, 'O', None]]
        self.assertEqual(GameChecker.check_winner(board), 'O', "O should win vertically on middle column")

        # Diagonal win for 'X'
        board.board = [['X', None, None], [None, 'X', None], [None, None, 'X']]
        self.assertEqual(GameChecker.check_winner(board), 'X', "X should win diagonally")

    def test_is_draw(self):
        # Test draw scenario where no spaces are left and no winner
        board = Board()
        board.board = [['X', 'O', 'X'], ['X', 'X', 'O'], ['O', 'X', 'O']]
        self.assertTrue(GameChecker.is_draw(board), "The board should be a draw with no spaces left and no winner")

        # Test not a draw scenario with empty spaces
        board.board = [['X', 'O', 'X'], ['X', None, 'O'], ['O', 'X', 'O']]
        self.assertFalse(GameChecker.is_draw(board), "The board should not be a draw as there are moves left")
