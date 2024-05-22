from core.board_9D import Board_9D


class MoveRuleStrategy:
    def next_board(self, board_position, cell_position, current_board: Board_9D):
        """
        Determine the next board to play on based on the last move.
        :param last_move: A tuple (row, col) representing the last move made on a board.
        :return: A tuple (next_row, next_col) indicating the next board to play on.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")


class StandardUltimateTicTacToeRule(MoveRuleStrategy):
    def next_board(self, board_position, cell_position, current_board: Board_9D):
        """
        Implements the standard Ultimate Tic-Tac-Toe rule:
        The next board is determined directly by the cell's position in the current board.
        """
        if current_board.board[cell_position[0]][cell_position[1]].is_full():  # Assuming an is_full method exists
            return None
        return cell_position  # The next board's position is the same as the cell's position in the current board.
