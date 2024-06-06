from core.game_checker import GameChecker
from core.board_9D import Board_9D, Board

class GameChecker9D:
    @staticmethod
    def check_winner_9d(board_9d_instance: Board_9D) -> str:
        # Assess each 3x3 board and collect their results in a new 3x3 grid
        results = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                board_instance = board_9d_instance.board[r][c]
                winner = GameChecker.check_winner(board_instance)
                if winner:
                    results[r][c] = winner
                else:
                    # Check for draw in the individual board
                    if GameChecker.is_draw(board_instance):
                        results[r][c] = None  # None for Draw

        return GameChecker.check_winner(Board(results))
