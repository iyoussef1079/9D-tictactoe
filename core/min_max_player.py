import copy

from core.ai_player import AIPlayer
from core.game_checker import GameChecker
from core.game_checker_9d import GameChecker9D


class MinimaxAIPlayer(AIPlayer):
    def __init__(self, name, symbol, max_depth=5):
        super().__init__(name, symbol)
        self.max_depth = max_depth

    def get_move(self, game_controller_instance):
        best_score = float('-inf')
        best_move = None
        player_symbol = self.symbol
        opponent_symbol = 'O' if player_symbol == 'X' else 'X'
        
        for move in generate_possible_moves(game_controller_instance.board, game_controller_instance.next_board):
            board_copy = copy.deepcopy(game_controller_instance.board)
            board_copy.place_piece(move[0], move[1], player_symbol)
            next_sub_board = move[1] if not GameChecker.check_winner(board_copy.board[move[0][0]][move[0][1]]) else None
            move_score = minimax(board_copy, 0, False, player_symbol, opponent_symbol, next_sub_board, self.max_depth)
            
            if move_score > best_score:
                best_score = move_score
                best_move = move
        
        return best_move

def evaluate_board(board_9d, player_symbol):
    opponent_symbol = 'O' if player_symbol == 'X' else 'X'
    
    # Check if the game is won by either player
    if GameChecker9D.check_winner_9d(board_9d) == player_symbol:
        return 1
    elif GameChecker9D.check_winner_9d(board_9d) == opponent_symbol:
        return -1

    # Evaluate the state of each sub-board
    score = 0
    for r in range(3):
        for c in range(3):
            sub_board = board_9d.board[r][c]
            if GameChecker.check_winner(sub_board) == player_symbol:
                score += 1
            elif GameChecker.check_winner(sub_board) == opponent_symbol:
                score -= 1

    return score

def generate_possible_moves(board_9d, next_board):
    moves = []
    if next_board:
        r, c = next_board
        if GameChecker.check_winner(board_9d.board[r][c]) is None:  # Check if the sub-board is not already won
            for cr in range(3):
                for cc in range(3):
                    if board_9d.board[r][c].board[cr][cc] is None:
                        moves.append(((r, c), (cr, cc)))
    else:
        for r in range(3):
            for c in range(3):
                if GameChecker.check_winner(board_9d.board[r][c]) is None:  # Check if the sub-board is not already won
                    for cr in range(3):
                        for cc in range(3):
                            if board_9d.board[r][c].board[cr][cc] is None:
                                moves.append(((r, c), (cr, cc)))
    return moves

def minimax(board_9d, depth, is_maximizing, player_symbol, opponent_symbol, next_board, max_depth):
    score = evaluate_board(board_9d, player_symbol)
    if abs(score) == 1 or depth == max_depth:
        return score
    
    if board_9d.is_full():
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for move in generate_possible_moves(board_9d, next_board):
            board_copy = copy.deepcopy(board_9d)
            board_copy.place_piece(move[0], move[1], player_symbol)
            next_sub_board = move[1] if not GameChecker.check_winner(board_copy.board[move[0][0]][move[0][1]]) else None
            best_score = max(best_score, minimax(board_copy, depth + 1, False, player_symbol, opponent_symbol, next_sub_board, max_depth))
        return best_score
    else:
        best_score = float('inf')
        for move in generate_possible_moves(board_9d, next_board):
            board_copy = copy.deepcopy(board_9d)
            board_copy.place_piece(move[0], move[1], opponent_symbol)
            next_sub_board = move[1] if not GameChecker.check_winner(board_copy.board[move[0][0]][move[0][1]]) else None
            best_score = min(best_score, minimax(board_copy, depth + 1, True, player_symbol, opponent_symbol, next_sub_board, max_depth))
        return best_score