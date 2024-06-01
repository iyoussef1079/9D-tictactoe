from typing import Any, List

from pydantic import BaseModel

from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D
from core.rule import StandardUltimateTicTacToeRule, MoveRuleStrategy
from core.exceptions import MoveRuleException

class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol  # 'X' or 'O'

class GameState(BaseModel):
    game_id: str
    boards: Any
    current_player: Any
    next_board: Any = None
    game_over: Any = False


class GameController:
    def __init__(self, game_id: str, board_9d_instance: Board_9D, game_checker_9d_instance: GameChecker9D, rule: MoveRuleStrategy):
        self.game_id = game_id
        self.board = board_9d_instance
        self.game_checker = game_checker_9d_instance
        self.players = {
            'X': Player(name="1", symbol='X'),
            'O': Player(name="2", symbol='O')
        }
        self.current_player = self.players['X']
        self.rule = rule
        self.next_board = None

    def switch_player(self):
        """Switch the current player between 'X' and 'O'."""
        self.current_player = self.players['O'] if self.current_player == self.players['X'] else self.players['X']

    def play_move(self, board_position, cell_position):
        """Place a piece on the board and switch turns."""
        if self.next_board and board_position != self.next_board:
            raise MoveRuleException()
        print(f"Player {self.current_player.name} ({self.current_player.symbol}) plays at {board_position} {cell_position}")
        self.board.place_piece(board_position, cell_position, self.current_player.symbol)
        self.next_board = self.rule.next_board(board_position, cell_position, self.board)
        self.switch_player()

        return self.check_game_over()

    def check_game_over(self):
        return self.game_checker.check_winner_9d(self.board)

    def get_state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            boards=self.board.to_serializable(),
            current_player=self.current_player.symbol,
            next_board=self.next_board,
            game_over=self.check_game_over()
        )