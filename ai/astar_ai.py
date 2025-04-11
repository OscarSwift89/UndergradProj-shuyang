# ai/astar_ai.py
import numpy as np
import heapq
import random
from .move_utils import get_valid_moves, get_jump_moves

class AStarAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_move(self, board):
        """
        对每个己方棋子（随机打乱顺序），如果不在目标区域，则尝试使用 A* 搜索到目标区域的完整路径，
        若能找到，则返回路径上的第一步；若无法找到完整路径，则退化为贪心策略：直接选择让棋子更接近目标区域的走法。
        如果所有棋子都在目标区域，或没有任何合法移动，则返回 None。
        """
        positions = [tuple(pos) for pos in np.argwhere(board == self.player_id)]
        random.shuffle(positions)
        # 尝试A*搜索完整路径
        for pos in positions:
            if self.in_target_area(pos):
                continue
            path = self.a_star(pos, board)
            if path is not None and len(path) >= 2:
                # 找到完整路径，直接返回第一步移动
                return (path[0], path[1])
        # 若A*未找到完整路径，则使用后备策略：遍历所有合法移动，选择启发值最小的走法（即靠近目标区域）
        best_move = None
        best_h = float('inf')
        for pos in positions:
            if self.in_target_area(pos):
                continue
            for move in get_valid_moves(pos, board) + get_jump_moves(pos, board):
                h = self.heuristic(move)
                if h < best_h:
                    best_h = h
                    best_move = (pos, move)
        return best_move

    def a_star(self, start, board):
        """
        采用 A* 算法从 start 位置搜索一条通往目标区域的路径。
        由于目标区域可能被占，要求目标为一个空格且位于目标区域内。
        如果找到，则返回从 start 到目标空格的路径（列表）；否则返回 None。
        """
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start), start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            current_f, current = heapq.heappop(open_set)
            # 终止条件：如果在目标区域内且该格为空（合法落脚点），则算作到达目标
            if self.in_target_area(current) and board[current] == 0:
                return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current, board):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor)
                    heapq.heappush(open_set, (f, neighbor))
        return None

    def heuristic(self, pos):
        """
        曼哈顿距离启发函数：
          - 对于玩家1，目标点取 (9,9)（目标区域的左上角）
          - 对于玩家2，目标点取 (2,2)
        """
        if self.player_id == 1:
            target = (9, 9)
        else:
            target = (2, 2)
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def reconstruct_path(self, came_from, current):
        """
        根据 came_from 字典回溯获得从起点到 current 的路径（列表形式）。
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def get_neighbors(self, pos, board):
        """
        使用工具函数获得所有合法的相邻走法（包括基础移动和跳跃）。
        """
        return get_valid_moves(pos, board) + get_jump_moves(pos, board)

    def in_target_area(self, pos):
        """
        判断指定位置是否在目标区域内：
          - 对于玩家1，目标区域：行号 >= 9 且列号 >= 9
          - 对于玩家2，目标区域：行号 < 3 且列号 < 3
        """
        if self.player_id == 1:
            return pos[0] >= 9 and pos[1] >= 9
        else:
            return pos[0] < 3 and pos[1] < 3
