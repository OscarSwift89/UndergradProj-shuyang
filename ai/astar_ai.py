# ai/astar_ai.py
import numpy as np
import heapq
import random
from .move_utils import get_valid_moves, get_jump_moves

class AStarAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_move(self, board):
        positions = [tuple(pos) for pos in np.argwhere(board == self.player_id)]
        random.shuffle(positions)
        for pos in positions:
            if self.in_target_area(pos):
                continue
            path = self.a_star(pos, board)
            if path is not None and len(path) >= 2:
                return (path[0], path[1])
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
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start), start))
        came_from = {}
        g_score = {start: 0}
        while open_set:
            current_f, current = heapq.heappop(open_set)
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
        if self.player_id == 1:
            target = (9, 9)
        elif self.player_id == 2:
            target = (9, 0)
        elif self.player_id == 3:
            target = (0, 9)
        elif self.player_id == 4:
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
        return get_valid_moves(pos, board) + get_jump_moves(pos, board)

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
