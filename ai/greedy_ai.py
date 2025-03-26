import numpy as np
import random

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id
        
    def choose_move(self, board):
        """贪心算法：选择最接近目标区域的移动，
        同时考虑基础移动和跳跃移动。
        如果有多个得分相同的选择，则由于顺序随机化，可以有一定的多样性。"""
        best_score = float('inf')
        best_move = None
        
        # 获取所有己方棋子位置并随机打乱顺序
        positions = list(np.argwhere(board == self.player_id))
        random.shuffle(positions)
        
        for pos in positions:
            pos = tuple(pos)
            # 同时获取基础移动和跳跃移动
            valid_moves = self.get_valid_moves(pos, board)
            jump_moves = self.get_jump_moves(pos, board)
            all_moves = valid_moves + jump_moves
            for move in all_moves:
                score = self.calculate_score(move)
                if score < best_score:
                    best_score = score
                    best_move = (pos, move)
        return best_move if best_move else None
    
    def calculate_score(self, position):
        """曼哈顿距离作为评估函数，目标区域为对角区域"""
        if self.player_id == 1:
            target = (16, 16)  # 玩家1目标：右下角
        else:
            target = (0, 0)    # 玩家2目标：左上角
        return abs(position[0] - target[0]) + abs(position[1] - target[1])
    
    def get_valid_moves(self, pos, board):
        """返回基础移动（上下左右）"""
        x, y = pos
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 17 and 0 <= ny < 17 and board[nx, ny] == 0:
                moves.append((nx, ny))
        return moves
    
    def get_jump_moves(self, pos, board):
        """返回跳跃移动：检查八个方向，如果相邻有棋子且跳后的位置为空"""
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
