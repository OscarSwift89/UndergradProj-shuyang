# ai/minimax_ai.py
import numpy as np
import random
from .move_utils import get_all_moves, free_up_target_entry

class MinimaxAI:
    def __init__(self, player_id, depth=2):
        self.player_id = player_id
        self.depth = depth

    def choose_move(self, board):
        move_to_free = free_up_target_entry(board, self.player_id)
        if move_to_free:
            return move_to_free
        
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
        # 为简化起见，固定选择一个对手（例如：如果自己不是 1 则对手用 1，否则用 2）
        opp = 1 if self.player_id != 1 else 2
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
        if self.player_id == 1:
            my_target = (11, 11)
        elif self.player_id == 2:
            my_target = (11, 0)
        elif self.player_id == 3:
            my_target = (0, 11)
        elif self.player_id == 4:
            my_target = (0, 0)
        my_pieces = np.argwhere(board == self.player_id)
        my_distance = sum([abs(p[0] - my_target[0]) + abs(p[1] - my_target[1]) for p in my_pieces])
        return -my_distance

    def terminal(self, board):
        p1_done = np.count_nonzero(board[9:12, 9:12] == 1) == 9
        p2_done = np.count_nonzero(board[9:12, 0:3] == 2) == 9
        p3_done = np.count_nonzero(board[0:3, 9:12] == 3) == 9
        p4_done = np.count_nonzero(board[0:3, 0:3] == 4) == 9
        return p1_done or p2_done or p3_done or p4_done
