from abc import ABC, abstractmethod

import random


class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol  # 'X' or 'O'

class AIPlayer(Player):
    def __init__(self, name, symbol):
        super().__init__(name, symbol)

    @abstractmethod
    def get_move(self, game_controller_instance):
        pass

class RandomAIPlayer(AIPlayer):
    def get_move(self, game_controller_instance):
        available_moves = game_controller_instance.get_available_moves()
        if available_moves:
            return random.choice(available_moves)
        return None
