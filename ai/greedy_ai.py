# ai/greedy_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves, free_up_target_entry, get_continuous_jump_moves

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_move(self, board):
        """
        ① 优先尝试腾挪目标区域入口，若入口被堵则先返回腾挪动作。
        ② 判断是否存在外部（未进入目标区域）的棋子：
             - 有：只考虑外部棋子的走法，以促使外部棋子进入目标区域。
             - 无：则调整目标区域内但未稳定的棋子，使其进一步深入目标区域，以腾出入口。
        ③ 生成候选走法时，除 get_valid_moves 与 get_jump_moves 外，
             同时调用 get_continuous_jump_moves，提取连续跳跃的最终落点，也作为候选走法。
        ④ 根据每个候选走法到深层目标的曼哈顿距离改善情况选择最优走法。
        """
        # ① 优先腾挪目标入口
        move_to_free = free_up_target_entry(board, self.player_id)
        if move_to_free:
            return move_to_free

        all_positions = [tuple(pos) for pos in np.argwhere(board == self.player_id)]

        # ② 筛选出在目标区域外的棋子，若存在则只考虑这些棋子，否则考虑未稳定的棋子
        outside_positions = [pos for pos in all_positions if not self.in_target_area(pos)]
        if outside_positions:
            positions_to_consider = outside_positions
        else:
            positions_to_consider = [pos for pos in all_positions if not self.in_stable_area(pos)]

        best_move = None
        best_improvement = -float('inf')
        fallback_move = None
        best_fallback = float('inf')
        random.shuffle(positions_to_consider)

        for pos in positions_to_consider:
            # 如果棋子已在目标区域且已稳定，则不考虑移动它
            if self.in_target_area(pos) and self.in_stable_area(pos):
                continue

            # ③ 候选走法：
            # 先取基础移动和单步跳跃
            candidate_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            # 加上连续跳跃（等距跳）走法，get_continuous_jump_moves 返回的是多个路径，每个路径的最后一个点作为落点
            jump_paths = get_continuous_jump_moves(pos, board)
            for path in jump_paths:
                candidate_moves.append(path[-1])
            
            # 如果该棋子已在目标区域但尚未稳定，则只考虑移动后依然在目标区域的走法
            if self.in_target_area(pos):
                candidate_moves = [m for m in candidate_moves if self.in_target_area(m)]
            
            current_score = self.calculate_score(pos)
            for candidate in candidate_moves:
                new_score = self.calculate_score(candidate)
                improvement = current_score - new_score  # 正数表示改善
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_move = (pos, candidate)
                if new_score < best_fallback:
                    best_fallback = new_score
                    fallback_move = (pos, candidate)
        
        return best_move if best_move is not None else fallback_move

    def in_target_area(self, pos):
        """
        判断位置是否在目标区域内：
          - 对于玩家1：行号 ≥ 9 且列号 ≥ 9；
          - 对于玩家2：行号 < 3 且列号 < 3。
        """
        if self.player_id == 1:
            return pos[0] >= 9 and pos[1] >= 9
        else:
            return pos[0] < 3 and pos[1] < 3

    def in_stable_area(self, pos):
        """
        判断位置是否处于目标区域的深层（稳定区域）：
          - 对于玩家1：行号 ≥ 10 且列号 ≥ 10；
          - 对于玩家2：行号 ≤ 1 且列号 ≤ 1。
        """
        if self.player_id == 1:
            return pos[0] >= 10 and pos[1] >= 10
        else:
            return pos[0] <= 1 and pos[1] <= 1

    def calculate_score(self, pos):
        """
        计算位置 pos 到深层目标的曼哈顿距离作为评分：
          - 对于玩家1：深层目标取 (11,11)；
          - 对于玩家2：深层目标取 (0,0)。
        分数越低表示位置越理想。
        """
        if self.player_id == 1:
            deep_target = (11, 11)
        else:
            deep_target = (0, 0)
        return abs(pos[0] - deep_target[0]) + abs(pos[1] - deep_target[1])
