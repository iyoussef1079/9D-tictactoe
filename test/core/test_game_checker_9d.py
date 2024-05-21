import unittest
from core.board_9D import Board_9D, Board
from core.game_checker_9d import GameChecker9D

class TestGameChecker9D(unittest.TestCase):

    def setUp(self):
        # Create a 9D board where each board is initially set with no winners
        self.board_9d = Board_9D()
        for r in range(3):
            for c in range(3):
                self.board_9d.board[r][c] = Board()

    def test_winner_across_top_row(self):
        # Set up a win condition across the top row of the 9D board
        for c in range(3):
            self.board_9d.board[0][c].board = [['X', 'X', 'X'], [None, None, None], [None, None, None]]

        self.assertEqual(GameChecker9D.check_winner_9d(self.board_9d), 'X', "X should win with a horizontal line across the top row of the 9D board")

    def test_mixed_results_no_9d_winner(self):
        # Set up mixed results without a clear 9D winner
        self.board_9d.board[0][0].board = [['X', 'X', 'X'], [None, None, None], [None, None, None]]
        self.board_9d.board[0][1].board = [['O', 'O', 'O'], [None, None, None], [None, None, None]]
        self.board_9d.board[0][2].board = [['X', 'X', 'X'], [None, None, None], [None, None, None]]
        self.board_9d.board[1][1].board = [['O', 'O', 'O'], [None, None, None], [None, None, None]]

        self.assertIsNone(GameChecker9D.check_winner_9d(self.board_9d), "There should be no 9D winner with mixed individual board results")

