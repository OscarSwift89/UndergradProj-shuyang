import numpy as np
import random

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id
        
    def choose_move(self, board):
        """
        贪心算法：选择使棋子距离目标区域曼哈顿距离最小的移动，
        对于已进入目标区域的棋子，只考虑留在目标区域内的移动。
        """
        best_score = float('inf')
        best_move = None
        
        # 随机打乱己方所有棋子的位置顺序，防止总是移动同一个棋子
        positions = list(np.argwhere(board == self.player_id))
        random.shuffle(positions)
        
        for pos in positions:
            pos = tuple(pos)
            # 如果该棋子已在目标区域，只考虑移动后仍在目标区域内的情况
            if self.in_target_area(pos):
                valid_moves = [m for m in self.get_valid_moves(pos, board) if self.in_target_area(m)]
                jump_moves = [m for m in self.get_jump_moves(pos, board) if self.in_target_area(m)]
            else:
                valid_moves = self.get_valid_moves(pos, board)
                jump_moves = self.get_jump_moves(pos, board)
            all_moves = valid_moves + jump_moves
            for move in all_moves:
                score = self.calculate_score(move)
                if score < best_score:
                    best_score = score
                    best_move = (pos, move)
        return best_move if best_move else None

    def in_target_area(self, pos):
        """判断指定位置是否在目标区域内"""
        if self.player_id == 1:
            # 玩家1的目标区域：右下角 4x4（索引 13-16）
            return pos[0] >= 13 and pos[1] >= 13
        else:
            # 玩家2的目标区域：左上角 4x4（索引 0-3）
            return pos[0] < 4 and pos[1] < 4

    def calculate_score(self, position):
        """使用曼哈顿距离作为评估函数，距离目标越近分数越低"""
        if self.player_id == 1:
            target = (16, 16)
        else:
            target = (0, 0)
        return abs(position[0] - target[0]) + abs(position[1] - target[1])
    
    def get_valid_moves(self, pos, board):
        """返回基础移动（上下左右）的合法位置"""
        x, y = pos
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 17 and 0 <= ny < 17 and board[nx, ny] == 0:
                moves.append((nx, ny))
        return moves
    
    def get_jump_moves(self, pos, board):
        """返回跳跃移动：检查八个方向，如果相邻有棋子且跳后的落脚点为空"""
        x, y = pos
        jumps = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2 * dx, y + 2 * dy
            if 0 <= midx < 17 and 0 <= midy < 17 and board[midx, midy] != 0:
                if 0 <= landingx < 17 and 0 <= landingy < 17 and board[landingx, landingy] == 0:
                    jumps.append((landingx, landingy))
        return jumps
