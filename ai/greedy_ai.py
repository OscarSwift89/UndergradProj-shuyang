import numpy as np  # 添加这一行
import random

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id
        
    def choose_move(self, board):
        """贪心算法：选择最接近目标区域的移动"""
        best_score = float('inf')
        best_move = None
        
        # 获取所有己方棋子位置
        positions = np.argwhere(board == self.player_id)
        
        for pos in positions:
            valid_moves = self.get_valid_moves(pos, board)
            for move in valid_moves:
                # 计算得分（距离目标区域的曼哈顿距离）
                score = self.calculate_score(move)
                if score < best_score:
                    best_score = score
                    best_move = (tuple(pos), move)
        
        return best_move if best_move else None
    
    def calculate_score(self, position):
        """目标区域为对角区域"""
        if self.player_id == 1:
            target = (16, 16)  # 右下角
        else:
            target = (0, 0)    # 左上角
        return abs(position[0]-target[0]) + abs(position[1]-target[1])
    
    def get_valid_moves(self, pos, board):
        x, y = pos
        moves = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 17 and 0 <= ny < 17 and board[nx, ny] == 0:
                moves.append((nx, ny))
        return moves