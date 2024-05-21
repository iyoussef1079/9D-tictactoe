import json

class Board:
    def __init__(self, board=None) -> None:
        if board is not None:
            assert len(board) == 3 and all(len(row) == 3 for row in board), "Board must be 3x3"
        self.board = [[None for _ in range(3)] for _ in range(3)] if board is None else board

    def to_serializable(self):
        """Prepare the board for serialization."""
        return self.board

    def place_piece(self, x, y, piece):
        """Place a piece on the board."""
        self.board[x][y] = piece

class Board_9D:
    def __init__(self) -> None:
        self.board = [[Board() for _ in range(3)] for _ in range(3)]

    def to_json(self):
        """Convert the 9D board to a JSON string."""
        return json.dumps(self.board, default=lambda o: o.to_serializable() if isinstance(o, Board) else o.__dict__)


    def to_serializable(self):
        """Prepare the 9D board for serialization."""
        return [[board.to_serializable() for board in row] for row in self.board]

    def place_piece(self, x, y, z, w, piece):
        """Place a piece on the board.
        x, y: The 3x3 board coordinates
        z, w: The piece coordinates within the 3x3 board
        piece: The piece to place
        """
        self.board[x][y].place_piece(z, w, piece)