from core.board_9D import Board

class GameChecker:
    @staticmethod
    def check_winner(board_instance: Board):
        # Fetch board state
        board = board_instance.to_serializable()

        # Check rows, columns, and diagonals for a winner
        lines = board  # Rows
        lines += [[board[r][c] for r in range(3)] for c in range(3)]  # Columns
        lines += [[board[i][i] for i in range(3)]]  # Main diagonal
        lines += [[board[i][2-i] for i in range(3)]]  # Secondary diagonal

        for line in lines:
            if line[0] is not None and all(cell == line[0] for cell in line):
                return line[0]  # Return 'X' or 'O' as winner
        return None

    @staticmethod
    def is_draw(board_instance: Board):
        # Fetch board state
        board = board_instance.to_serializable()

        # Check if the board is full and no winner
        if all(cell is not None for row in board for cell in row):
            return GameChecker.check_winner(board_instance) is None
        return False
