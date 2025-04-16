# ai/greedy_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves, free_up_target_entry

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def get_deep_target(self):
        if self.player_id == 1:
            return (11, 11)
        elif self.player_id == 2:
            return (11, 0)
        elif self.player_id == 3:
            return (0, 11)
        elif self.player_id == 4:
            return (0, 0)
        return None

    def in_target_area(self, pos):
        if self.player_id == 1:
            return pos[0] >= 9 and pos[1] >= 9
        elif self.player_id == 2:
            return pos[0] >= 9 and pos[1] < 3
        elif self.player_id == 3:
            return pos[0] < 3 and pos[1] >= 9
        elif self.player_id == 4:
            return pos[0] < 3 and pos[1] < 3
        return False

    def in_stable_area(self, pos):
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
        # 曼哈顿距离作为评分，距离越短表示位置越理想
        deep_target = self.get_deep_target()
        return abs(pos[0] - deep_target[0]) + abs(pos[1] - deep_target[1])

    def choose_move(self, board):
        deep_target = self.get_deep_target()
        # 第一步：如果深层目标单元为空，尝试直接将某个棋子移动到深层目标上
        if board[deep_target] == 0:
            positions = [tuple(p) for p in np.argwhere(board == self.player_id)]
            for pos in positions:
                valid_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
                if deep_target in valid_moves:
                    return (pos, deep_target)
        # 第二步：尝试调用腾挪入口的走法（free_up_target_entry）
        move_to_free = free_up_target_entry(board, self.player_id)
        if move_to_free:
            return move_to_free

        # 第三步：正常的策略，根据各棋子到深层目标的曼哈顿距离改善情况选择最优走法
        all_positions = [tuple(p) for p in np.argwhere(board == self.player_id)]
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
            candidate_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            if self.in_target_area(pos):
                candidate_moves = [m for m in candidate_moves if self.in_target_area(m)]
            
            current_score = self.calculate_score(pos)
            for candidate in candidate_moves:
                new_score = self.calculate_score(candidate)
                improvement = current_score - new_score
                if not self.in_target_area(pos) and self.in_target_area(candidate):
                    improvement += bonus
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_move = (pos, candidate)
                if new_score < best_fallback:
                    best_fallback = new_score
                    fallback_move = (pos, candidate)
        return best_move if best_move is not None else fallback_move
