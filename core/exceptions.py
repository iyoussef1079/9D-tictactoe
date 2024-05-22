class CellOccupiedError(Exception):
    """Exception raised when trying to place a piece in an occupied cell."""

    def __init__(self, message="This cell is already occupied"):
        self.message = message
        super().__init__(self.message)

class MoveRuleException(Exception):
    """Exception raised when an invalid board is chosen based on the last move."""

    def __init__(self, message="Rule violation: Current rule does not allow this move"):
        self.message = message
        super().__init__(self.message)