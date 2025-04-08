import numpy as np
import random

class MinimaxAI:
    def __init__(self, player_id, depth=2):
        self.player_id = player_id
        self.depth = depth

    def choose_move(self, board):
        moves = self.get_all_moves(board, self.player_id)
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
        moves = self.get_all_moves(board, self.player_id)
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
        moves = self.get_all_moves(board, opp)
        if not moves:
            return self.evaluate(board)
        for move in moves:
            new_board = self.simulate_move(board, move)
            value = min(value, self.max_value(new_board, depth - 1, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

    def evaluate(self, board):
        # 简单使用所有棋子到目标区域的曼哈顿距离之和来作为评估
        if self.player_id == 1:
            my_target = (16, 16)
            opp_target = (0, 0)
        else:
            my_target = (0, 0)
            opp_target = (16, 16)
        my_pieces = np.argwhere(board == self.player_id)
        opp_pieces = np.argwhere(board == (2 if self.player_id == 1 else 1))
        my_distance = sum([abs(p[0] - my_target[0]) + abs(p[1] - my_target[1]) for p in my_pieces])
        opp_distance = sum([abs(p[0] - opp_target[0]) + abs(p[1] - opp_target[1]) for p in opp_pieces])
        # 返回对手距离减去己方距离，己方距离越小越好
        return opp_distance - my_distance

    def get_all_moves(self, board, player_id):
        moves = []
        positions = list(np.argwhere(board == player_id))
        for pos in positions:
            pos = tuple(pos)
            moves += self.get_valid_moves(pos, board)
            moves += self.get_jump_moves(pos, board)
        return moves

    def simulate_move(self, board, move):
        new_board = board.copy()
        from_pos, to_pos = move
        new_board[to_pos] = new_board[from_pos]
        new_board[from_pos] = 0
        return new_board

    def get_valid_moves(self, pos, board):
        x, y = pos
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 17 and 0 <= ny < 17 and board[nx, ny] == 0:
                moves.append((pos, (nx, ny)))
        return moves

    def get_jump_moves(self, pos, board):
        x, y = pos
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2 * dx, y + 2 * dy
            if 0 <= midx < 17 and 0 <= midy < 17 and board[midx, midy] != 0:
                if 0 <= landingx < 17 and 0 <= landingy < 17 and board[landingx, landingy] == 0:
                    moves.append((pos, (landingx, landingy)))
        return moves

    def terminal(self, board):
        # 胜利条件: 当任一玩家所有棋子进入对方阵营
        if self.player_id == 1:
            return np.count_nonzero(board[-4:, -4:] == 1) == 16 or np.count_nonzero(board[0:4, 0:4] == 2) == 16
        else:
            return np.count_nonzero(board[0:4, 0:4] == 2) == 16 or np.count_nonzero(board[-4:, -4:] == 1) == 16
