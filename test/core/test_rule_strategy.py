import unittest
from unittest.mock import MagicMock
from core.board_9D import Board_9D, Board
from core.rule import StandardUltimateTicTacToeRule, MoveRuleStrategy


class TestStandardUltimateTicTacToeRule(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.rule = StandardUltimateTicTacToeRule()
        self.board_9d = Board_9D()
        self.board_9d.board = [[MagicMock(spec=Board) for _ in range(3)] for _ in range(3)]
        for row in self.board_9d.board:
            for board in row:
                board.is_full.return_value = False

    def test_next_board_position_not_full(self):
        # Test scenario where the next board is not full
        board_position = (0, 0)
        cell_position = (1, 2)
        next_board = self.rule.next_board(board_position, cell_position, self.board_9d)
        self.assertEqual(next_board, cell_position, "The next board should be determined by the cell position.")

    def test_next_board_position_when_full(self):
        # Scenario where the next board determined by the last move is full
        self.board_9d.board[1][2].is_full.return_value = True
        board_position = (0, 0)
        cell_position = (1, 2)
        next_board = self.rule.next_board(board_position, cell_position, self.board_9d)
        self.assertIsNone(next_board, "Next board should be None if the determined board is full.")