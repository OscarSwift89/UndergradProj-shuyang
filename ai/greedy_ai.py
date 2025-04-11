# ai/greedy_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id
        
    def choose_move(self, board):
        """
        遍历所有己方棋子（随机顺序），若棋子不在目标区域，
        对其所有合法走法计算“改善值”：当前与移动后目标区域曼哈顿距离的差值。
        优先选择改善值最大的移动；如果没有正改善的走法，则选择能使目标距离最低的走法。
        """
        best_move = None
        best_improvement = 0  # 正改善要求 > 0
        fallback_move = None
        best_fallback = float('inf')  # 用于记录最低目标距离
        positions = [tuple(pos) for pos in np.argwhere(board == self.player_id)]
        random.shuffle(positions)
        
        for pos in positions:
            # 若该棋子已经在目标区域，则跳过
            if self.in_target_area(pos):
                continue
            # 计算当前棋子距离目标区域的曼哈顿距离
            current_h = self.calculate_score(pos)
            candidate_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            for move in candidate_moves:
                new_h = self.calculate_score(move)
                improvement = current_h - new_h  # 希望这个值为正
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_move = (pos, move)
                # 同时记录整体最低的新启发值（作为后备选择）
                if new_h < best_fallback:
                    best_fallback = new_h
                    fallback_move = (pos, move)
        
        # 如果有正改善的移动，则返回该移动，否则返回整体最优的走法
        return best_move if best_move else fallback_move

    def in_target_area(self, pos):
        """
        判断指定位置是否处于目标区域：
          - 对于玩家1，目标区域：行号 ≥ 9 且列号 ≥ 9
          - 对于玩家2，目标区域：行号 < 3 且列号 < 3
        """
        if self.player_id == 1:
            return pos[0] >= 9 and pos[1] >= 9
        else:
            return pos[0] < 3 and pos[1] < 3

    def calculate_score(self, pos):
        """
        使用曼哈顿距离评估距离：
         - 对于玩家1，目标取棋盘最右下角 (11, 11)
         - 对于玩家2，目标取棋盘最左上角 (0, 0)
        分数越低表示离目标区域越近。
        """
        if self.player_id == 1:
            target = (11, 11)
        else:
            target = (0, 0)
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])
