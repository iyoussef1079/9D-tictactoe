from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D
from core.rule import StandardUltimateTicTacToeRule, MoveRuleStrategy
from core.exceptions import MoveRuleException

class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol  # 'X' or 'O'


class GameController:
    def __init__(self, game_id, board_9d_instance: Board_9D, game_checker_9d_instance: GameChecker9D, rule: MoveRuleStrategy):
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

    def start_game(self):
        """Start the game loop."""
        print("Starting 9D Tic-Tac-Toe game...")
        game_over = False
        while not game_over:
            # Print board state here if needed
            try:
                row = int(input("Enter row (0-2): "))
                col = int(input("Enter column (0-2): "))
                subrow = int(input("Enter sub-row (0-2): "))
                subcol = int(input("Enter sub-column (0-2): "))
                game_over = self.play_move((row, col), (subrow, subcol))
            except Exception as e:
                print(str(e))
                continue

    def get_state(self):
        return {
            'game_id': self.game_id,
            'boards': self.board.to_serializable(),
        }