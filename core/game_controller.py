from dataclasses import asdict, dataclass
from typing import Any, List, Set, Tuple

from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D, GameChecker
from core.rule import StandardUltimateTicTacToeRule, MoveRuleStrategy
from core.exceptions import AlreadyWinBoardException, MoveRuleException

class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol  # 'X' or 'O'

@dataclass
class GameState:
    game_id: str
    boards: List[List[List[List[str]]]]
    current_player: str
    next_board: Tuple[int, int] = None
    game_over: Any = False
    won_board: dict[str, List[Tuple[int, int]]] = None

    def __init__(self, game_id, boards, current_player, next_board, game_over, won_board=None):
        self.game_id = game_id
        self.boards = boards
        self.current_player = current_player
        self.next_board = next_board
        self.game_over = game_over
        self.won_board = won_board if won_board is not None else {'X': [], 'O': []}

    def to_dict(self):
        # Custom handling for non-serializable fields if necessary
        result = asdict(self)
        if self.next_board is not None:
            result['next_board'] = list(self.next_board)
        result['won_board'] = {key: [list(pos) for pos in value] for key, value in self.won_board.items()}
        return result


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
        self.won_board = {'X': [], 'O': []}  # Initialize the won_board dictionary

    def switch_player(self):
        """Switch the current player between 'X' and 'O'."""
        self.current_player = self.players['O'] if self.current_player == self.players['X'] else self.players['X']

    def play_move(self, board_position, cell_position):
        """Place a piece on the board and switch turns."""
        if self.next_board and board_position != self.next_board:
            raise MoveRuleException()
        elif GameChecker.check_winner(self.board.board[board_position[0]][board_position[1]]):
            raise AlreadyWinBoardException()

        print(f"Player {self.current_player.name} ({self.current_player.symbol}) plays at {board_position} {cell_position}")
        self.board.place_piece(board_position, cell_position, self.current_player.symbol)

        # Check if the board is won after the move
        if GameChecker.check_winner(self.board.board[board_position[0]][board_position[1]]):
            self.won_board[self.current_player.symbol].append(tuple(board_position))

        self.next_board = self.rule.next_board(board_position, cell_position, self.board)
        self.switch_player()

        return self.check_game_over()

    def check_game_over(self) -> str:
        return self.game_checker.check_winner_9d(self.board)

    def get_state(self) -> GameState:
        return GameState(
            game_id=self.game_id,
            boards=self.board.to_serializable(),
            current_player=self.current_player.symbol,
            next_board=self.next_board,
            game_over=self.check_game_over(),
            won_board=self.won_board  # Include won_board in the game state
        )