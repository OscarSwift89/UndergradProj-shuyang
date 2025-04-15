# ai/greedy_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves, free_up_target_entry

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_move(self, board):
        # 尝试腾挪目标区域入口（如果返回合法走法则直接使用）
        move_to_free = free_up_target_entry(board, self.player_id)
        if move_to_free:
            return move_to_free

        all_positions = [tuple(pos) for pos in np.argwhere(board == self.player_id)]
        # 优先考虑不在目标区域的棋子；若全部在目标区域，则考虑不在稳定区域的棋子
        outside_positions = [pos for pos in all_positions if not self.in_target_area(pos)]
        positions_to_consider = outside_positions if outside_positions else [pos for pos in all_positions if not self.in_stable_area(pos)]
        
        bonus = 20
        if outside_positions and len(outside_positions) == 1:
            bonus = 100

        best_move = None
        best_improvement = -float('inf')
        fallback_move = None
        best_fallback = float('inf')
        random.shuffle(positions_to_consider)
        
        for pos in positions_to_consider:
            if self.in_target_area(pos) and self.in_stable_area(pos):
                continue

            # 同时考虑合法单步移动与跳跃
            candidate_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            if self.in_target_area(pos):
                candidate_moves = [m for m in candidate_moves if self.in_target_area(m)]
            
            current_score = self.calculate_score(pos)
            for candidate in candidate_moves:
                new_score = self.calculate_score(candidate)
                improvement = current_score - new_score

                if (not self.in_target_area(pos)) and self.in_target_area(candidate):
                    improvement += bonus

                if improvement > best_improvement:
                    best_improvement = improvement
                    best_move = (pos, candidate)
                if new_score < best_fallback:
                    best_fallback = new_score
                    fallback_move = (pos, candidate)
        
        return best_move if best_move is not None else fallback_move

    def in_target_area(self, pos):
        if self.player_id == 1:
            return pos[0] >= 9 and pos[1] >= 9      # 玩家1目标：右下角
        elif self.player_id == 2:
            return pos[0] >= 9 and pos[1] < 3       # 玩家2目标：左下角
        elif self.player_id == 3:
            return pos[0] < 3 and pos[1] >= 9       # 玩家3目标：右上角
        elif self.player_id == 4:
            return pos[0] < 3 and pos[1] < 3        # 玩家4目标：左上角
        return False

    def in_stable_area(self, pos):
        # 定义各目标区域内部的深层（稳定）区域
        if self.player_id == 1:
            return pos[0] >= 10 and pos[1] >= 10
        elif self.player_id == 2:
            return pos[0] >= 10 and pos[1] <= 1
        elif self.player_id == 3:
            return pos[0] <= 1 and pos[1] >= 10
        elif self.player_id == 4:
            return pos[0] <= 1 and pos[1] <= 1
        return False

    def calculate_score(self, pos):
        if self.player_id == 1:
            deep_target = (11, 11)
        elif self.player_id == 2:
            deep_target = (11, 0)
        elif self.player_id == 3:
            deep_target = (0, 11)
        elif self.player_id == 4:
            deep_target = (0, 0)
        return abs(pos[0] - deep_target[0]) + abs(pos[1] - deep_target[1])
