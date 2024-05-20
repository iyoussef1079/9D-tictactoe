import json

class Board:
    def __init__(self) -> None:
        self.board = [[None for _ in range(3)] for _ in range(3)]

    def to_serializable(self):
        """Prepare the board for serialization."""
        return self.board

class Board_9D:
    def __init__(self) -> None:
        self.board = [[Board() for _ in range(3)] for _ in range(3)]

    def to_json(self):
        """Convert the 9D board to a JSON string."""
        return json.dumps(self.board, default=lambda o: o.to_serializable() if isinstance(o, Board) else o.__dict__)

    def to_serializable(self):
        """Prepare the 9D board for serialization."""
        return [[board.to_serializable() for board in row] for row in self.board]