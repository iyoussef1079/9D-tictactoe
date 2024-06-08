from keras.models import load_model
from keras.optimizers import Adam
import numpy as np
import copy

from core.ai_player import AIPlayer

class AlphaZeroAIPlayer(AIPlayer):
    def __init__(self, name, symbol, model_path):
        super().__init__(name, symbol)
        self.model = load_model(model_path, compile=False)
        optimizer = Adam(learning_rate=0.001)
        self.model.compile(optimizer=optimizer)
        self.mcts_search = 400
        self.cpuct = 2
        self.Q = {}
        self.Nsa = {}
        self.Ns = {}
        self.W = {}
        self.P = {}

    def get_move(self, game_controller_instance):
        board_array = self.board_to_array(game_controller_instance.board, game_controller_instance.next_board, 1 if self.symbol == 'X' else -1)
        action_probs = self.get_action_probs(board_array, game_controller_instance.next_board)

        action = int(np.argmax(action_probs))

        while True:
            move = self.decode_action(action, game_controller_instance.next_board)
            if move is not None:
                return move
            action_probs[action] = 0  # Invalidate the current action and find the next best
            action = int(np.argmax(action_probs))

    def decode_action(self, action, next_board):
        board_position = [int(action // 9 // 3), int(action // 9 % 3)]
        cell_position = [int(action % 9 // 3), int(action % 9 % 3)]
        if next_board and (board_position != next_board):
            return None  # Indicate invalid move
        return board_position, cell_position


    def board_to_array(self, board, next_board, player):
        array = np.zeros((9, 9))
        board_copy = board.to_serializable()
        board_copy = self.fill_winning_boards(board_copy)
        
        next_board_index = next_board[0] * 3 + next_board[1] if next_board else 9
        
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        sub_board_index = i * 3 + j
                        cell_value = board_copy[i][j][k][l]
                        if sub_board_index == next_board_index or next_board_index == 9:
                            if cell_value is None:
                                cell_value = 'v'  # Mark valid moves in the active sub-board or any if all are active
                        array[sub_board_index // 3 * 3 + k][sub_board_index % 3 * 3 + l] = self.letter_to_int(cell_value, player)
        
        print(array)
        return array

    def letter_to_int(self, letter, player):
        if letter == 'v':
            return 0.1
        elif letter is None:
            return 0
        elif letter == "X":
            return 1 * player
        elif letter == "O":
            return -1 * player

    def fill_winning_boards(self, board):
        new_board = copy.deepcopy(board)
        for i in range(3):
            for j in range(3):
                sub_board = new_board[i][j]
                if sub_board[1][1] == 'X':
                    new_board[i][j] = [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]]
                elif sub_board[1][1] == 'O':
                    new_board[i][j] = [["O", "O", "O"], ["O", "O", "O"], ["O", "O", "O"]]
        return new_board

    def get_action_probs(self, board_array, next_board):
        action_probs = self.model.predict(board_array.reshape(1, 9, 9))[0]
        
        # Ensure the action_probs is a 1D array
        if action_probs.shape == (1, 81):
            action_probs = action_probs.flatten()
        
        if action_probs.shape != (81,):
            raise ValueError(f"Unexpected action_probs shape: {action_probs.shape}")

        if next_board:
            next_board_index = next_board[0] * 3 + next_board[1]
            mask = np.zeros(81)
            for i in range(9):
                for j in range(9):
                    sub_board_index = (i // 3) * 3 + (j // 3)
                    if sub_board_index == next_board_index:
                        mask[i * 9 + j] = 1
            action_probs = action_probs * mask
        else:
            mask = np.ones(81)
            for i in range(9):
                for j in range(9):
                    sub_board_index = (i // 3) * 3 + (j // 3)
                    if self.board.board[sub_board_index // 3][sub_board_index % 3].is_full():
                        for k in range(9):
                            mask[sub_board_index * 9 + k] = 0
            action_probs = action_probs * mask

        if np.sum(action_probs) == 0:
            action_probs = mask

        return action_probs / np.sum(action_probs)

