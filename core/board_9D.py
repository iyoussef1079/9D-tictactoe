import json

from core.exceptions import CellOccupiedError

class Board:
    def __init__(self, board=None) -> None:
        if board is not None:
            assert len(board) == 3 and all(len(row) == 3 for row in board), "Board must be 3x3"
        self.board = [[None for _ in range(3)] for _ in range(3)] if board is None else board

    def to_serializable(self):
        """Prepare the board for serialization."""
        return self.board

    def place_piece(self, cell_position, piece):
        """Place a piece on the board."""
        if self.board[cell_position[0]][cell_position[0]] is not None:
            raise CellOccupiedError()
        self.board[cell_position[0]][cell_position[0]] = piece

    def is_full(self):
        """Check if the board is full."""
        return all(cell is not None for row in self.board for cell in row)

class Board_9D:
    def __init__(self) -> None:
        self.board = [[Board() for _ in range(3)] for _ in range(3)]

    def to_serializable(self):
        """Prepare the 9D board for serialization."""
        return [[board.to_serializable() for board in row] for row in self.board]

    def place_piece(self, board_position, cell_position, piece):
        """Place a piece on the board.
        x, y: The 3x3 board coordinates
        z, w: The piece coordinates within the 3x3 board
        piece: The piece to place
        """
        self.board[board_position[0]][board_position[1]].place_piece(cell_position, piece)