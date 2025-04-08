__all__ = ["AStarAI"]

import numpy as np
import heapq
import random

class AStarAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_move(self, board):
        # 对每个己方棋子，若未在目标区域内，则利用 A* 搜索寻找到目标区域的最短路径，
        # 返回路径上第一步的移动。（如果已经在目标区域内则不移动）
        positions = list(np.argwhere(board == self.player_id))
        random.shuffle(positions)
        best_first_move = None
        best_cost = float('inf')
        for pos in positions:
            pos = tuple(pos)
            if self.in_target_area(pos):
                continue
            path = self.a_star(pos, board)
            if path is not None and len(path) < best_cost:
                best_cost = len(path)
                # path[0] 为起点，path[1] 为第一步
                if len(path) >= 2:
                    best_first_move = (pos, path[1])
        return best_first_move if best_first_move else None

    def a_star(self, start, board):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            current_f, current = heapq.heappop(open_set)
            if self.in_target_area(current):
                return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current, board):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor)
                    heapq.heappush(open_set, (f_score, neighbor))
        return None

    def heuristic(self, pos):
        # 曼哈顿距离作为启发函数
        if self.player_id == 1:
            target = (16, 16)
        else:
            target = (0, 0)
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def get_neighbors(self, pos, board):
        return self.get_valid_moves(pos, board) + self.get_jump_moves(pos, board)

    def get_valid_moves(self, pos, board):
        x, y = pos
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 17 and 0 <= ny < 17 and board[nx, ny] == 0:
                moves.append((nx, ny))
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
                    moves.append((landingx, landingy))
        return moves

    def in_target_area(self, pos):
        if self.player_id == 1:
            # 玩家1目标区域：右下角 4x4（行和列索引 13~16）
            return pos[0] >= 13 and pos[1] >= 13
        else:
            return pos[0] < 4 and pos[1] < 4
