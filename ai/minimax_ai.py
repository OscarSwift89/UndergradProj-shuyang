# ai/minimax_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves, get_all_moves

class MinimaxAI:
    def __init__(self, player_id, depth=2):
        self.player_id = player_id
        self.depth = depth

    def choose_move(self, board):
        moves = get_all_moves(board, self.player_id)
        if not moves:
            return None
        best_val = -float('inf')
        best_move = None
        for move in moves:
            new_board = self.simulate_move(board, move)
            val = self.min_value(new_board, self.depth - 1, -float('inf'), float('inf'))
            if val > best_val:
                best_val = val
                best_move = move
        return best_move

    def max_value(self, board, depth, alpha, beta):
        if depth == 0 or self.terminal(board):
            return self.evaluate(board)
        value = -float('inf')
        moves = get_all_moves(board, self.player_id)
        if not moves:
            return self.evaluate(board)
        for move in moves:
            new_board = self.simulate_move(board, move)
            value = max(value, self.min_value(new_board, depth - 1, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def min_value(self, board, depth, alpha, beta):
        opp = 2 if self.player_id == 1 else 1
        if depth == 0 or self.terminal(board):
            return self.evaluate(board)
        value = float('inf')
        moves = get_all_moves(board, opp)
        if not moves:
            return self.evaluate(board)
        for move in moves:
            new_board = self.simulate_move(board, move)
            value = min(value, self.max_value(new_board, depth - 1, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

    def simulate_move(self, board, move):
        new_board = board.copy()
        from_pos, to_pos = move
        new_board[to_pos] = new_board[from_pos]
        new_board[from_pos] = 0
        return new_board

    def evaluate(self, board):
        # 简单使用所有棋子到目标区域的曼哈顿距离之和来作为评估
        if self.player_id == 1:
            my_target = (11, 11)
            opp_target = (0, 0)
        else:
            my_target = (0, 0)
            opp_target = (11, 11)
        my_pieces = np.argwhere(board == self.player_id)
        opp_pieces = np.argwhere(board == (2 if self.player_id == 1 else 1))
        my_distance = sum([abs(p[0] - my_target[0]) + abs(p[1] - my_target[1]) for p in my_pieces])
        opp_distance = sum([abs(p[0] - opp_target[0]) + abs(p[1] - opp_target[1]) for p in opp_pieces])
        return opp_distance - my_distance

    def terminal(self, board):
        if self.player_id == 1:
            return np.count_nonzero(board[-3:, -3:] == 1) == 9 or np.count_nonzero(board[0:3, 0:3] == 2) == 9
        else:
            return np.count_nonzero(board[0:3, 0:3] == 2) == 9 or np.count_nonzero(board[-3:, -3:] == 1) == 9
