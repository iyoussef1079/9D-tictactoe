from abc import ABC, abstractmethod


class AIPlayer(ABC):
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    @abstractmethod
    def get_move(self, game_controller_instance):
        pass

# Example of a Random AI (placeholder for actual AI logic)
import random

class RandomAIPlayer(AIPlayer):
    def get_move(self, game_controller_instance):
        # Placeholder logic: Choose a random empty cell
        available_moves = game_controller_instance.get_available_moves()
        if available_moves:
            return random.choice(available_moves)
        return None
