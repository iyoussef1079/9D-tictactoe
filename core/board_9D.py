from core.exceptions import CellOccupiedError
class Board:
    def __init__(self, board=None) -> None:
        if board is not None:
            assert len(board) == 3 and all(len(row) == 3 for row in board), "Board must be 3x3"
        self.board = [[None for _ in range(3)] for _ in range(3)] if board is None else board

    def to_serializable(self):
        """Prepare the board for serialization."""
        return [[cell for cell in row] for row in self.board]

    def place_piece(self, cell_position, piece):
        """Place a piece on the board."""
        row, col = cell_position
        if self.board[row][col] is not None:
            raise CellOccupiedError()
        self.board[row][col] = piece

    def is_full(self):
        """Check if the board is full."""
        return all(cell is not None for row in self.board for cell in row)

    def get_available_moves(self):
        """Get a list of available moves on the board."""
        return [(r, c) for r, row in enumerate(self.board) for c, cell in enumerate(row) if cell is None]

class Board_9D:
    def __init__(self) -> None:
        self.board = [[Board() for _ in range(3)] for _ in range(3)]

    def to_serializable(self):
        """Prepare the 9D board for serialization."""
        return [[board.to_serializable() for board in row] for row in self.board]

    def place_piece(self, board_position, cell_position, piece):
        """Place a piece on the board.
        board_position: The 3x3 board coordinates
        cell_position: The piece coordinates within the 3x3 board
        piece: The piece to place
        """
        board_row, board_col = board_position
        self.board[board_row][board_col].place_piece(cell_position, piece)

    def get_available_moves(self):
        """Get a list of available moves on the 9D board."""
        return [(r, c, cell_pos) for r, row in enumerate(self.board) for c, board in enumerate(row)
                for cell_pos in board.get_available_moves()]
    
    def is_full(self):
        """Check if the 9D board is full."""
        return all(board.is_full() for row in self.board for board in row)
