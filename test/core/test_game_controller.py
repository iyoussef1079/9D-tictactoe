import unittest
from unittest.mock import MagicMock
from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D
from core.rule import StandardUltimateTicTacToeRule, MoveRuleStrategy
from core.exceptions import MoveRuleException
from core.game_controller import GameController, Player

class TestGameController(unittest.TestCase):
    def setUp(self):
        self.board_9d = MagicMock(spec=Board_9D)
        self.game_checker = MagicMock(spec=GameChecker9D)
        self.rule = MagicMock(spec=MoveRuleStrategy)
        self.game_controller = GameController(self.board_9d, self.game_checker, self.rule)

    def test_switch_player(self):
        # Initially, player X starts
        self.assertEqual(self.game_controller.current_player.symbol, 'X')
        self.game_controller.switch_player()
        self.assertEqual(self.game_controller.current_player.symbol, 'O')
        self.game_controller.switch_player()
        self.assertEqual(self.game_controller.current_player.symbol, 'X')

    def test_play_move_valid(self):
        # Simulate a valid move
        self.game_controller.next_board = (1, 1)
        self.rule.next_board.return_value = (2, 2)  # Set the next board after move
        game_over = self.game_controller.play_move((1, 1), (0, 0))
        self.board_9d.place_piece.assert_called_once_with((1, 1), (0, 0), 'X')
        self.assertEqual(self.game_controller.next_board, (2, 2))

    def test_play_move_invalid_board(self):
        # Test moving to an incorrect board
        self.game_controller.next_board = (1, 1)
        with self.assertRaises(MoveRuleException):
            self.game_controller.play_move((2, 2), (0, 0))

    def test_game_over_check(self):
        # Simulate game over condition
        self.game_controller.next_board = (1, 1)
        self.rule.next_board.return_value = None
        self.game_checker.check_winner_9d.return_value = True
        game_over = self.game_controller.play_move((1, 1), (0, 0))
        self.assertTrue(game_over)