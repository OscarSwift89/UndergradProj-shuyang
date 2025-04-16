import numpy as np
import random
from collections import deque
from .move_utils import get_valid_moves, get_jump_moves

class BFSAgent:
    def __init__(self, player_id, max_depth=8):
        """
        :param player_id: 玩家ID
        :param max_depth: BFS最多搜索的深度，避免搜索过大造成卡顿
        """
        self.player_id = player_id
        self.max_depth = max_depth

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

    def calculate_distance_to_target(self, pos):
        # 简单用曼哈顿距离判断离目标角的远近
        if self.player_id == 1:
            target = (11, 11)
        elif self.player_id == 2:
            target = (11, 0)
        elif self.player_id == 3:
            target = (0, 11)
        else:  # player_id == 4
            target = (0, 0)
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def choose_move(self, board):
        positions = [tuple(pos) for pos in np.argwhere(board == self.player_id)]
        random.shuffle(positions)
        for pos in positions:
            # 若己方棋子已经在目标区，可根据策略决定是否继续搜索让它深入，简化起见此处直接跳过
            if self.in_target_area(pos):
                continue
            path = self.bfs_search(board, start=pos, max_depth=self.max_depth)
            if path is not None and len(path) >= 2:
                return (pos, path[1])
        return None

    def bfs_search(self, board, start, max_depth):
        """
        限深 BFS 搜索：在 <= max_depth 步/跳 内，尝试找到能进入目标区域的路径。
        若搜索完仍找不到，则选搜索到的最末层中“离目标最近”的位置作为 fallback。
        返回：若能直达目标区域，则返回整条路径，否则返回到 fallback 位置的路径。
        """
        from collections import deque
        queue = deque()
        visited = set()
        # 每个元素形如 (path, depth)
        queue.append(([start], 0))
        visited.add(start)

        best_path = None
        best_dist = self.calculate_distance_to_target(start)

        while queue:
            path, depth = queue.popleft()
            cur = path[-1]
            # 如果当前在目标区域且该单元为空 => 找到直达目标区
            if self.in_target_area(cur) and board[cur] == 0:
                return path  # 直接返回完整路径

            # 若深度已达上限，不再继续扩展
            if depth >= max_depth:
                # 记录一下离目标最近的位置作为 fallback
                dist = self.calculate_distance_to_target(cur)
                if dist < best_dist:
                    best_dist = dist
                    best_path = path
                continue

            # 获取当前位置所有合法下一步（单步+跳跃），在静态棋盘下
            next_moves = get_valid_moves(cur, board) + get_jump_moves(cur, board)
            for nxt in next_moves:
                if nxt not in visited:
                    visited.add(nxt)
                    new_path = path + [nxt]
                    queue.append((new_path, depth + 1))
                    # 同时更新 fallback
                    dist = self.calculate_distance_to_target(nxt)
                    if dist < best_dist:
                        best_dist = dist
                        best_path = new_path

        return best_path  # 若没搜到目标区，返回“离目标最近”的路径
