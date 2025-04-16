# ai/mcts_ai.py
import random
import math
import time
import numpy as np
from .move_utils import get_all_moves

class MCTSNode:
    def __init__(self, board_state, player_id, parent=None, move=None):
        self.board_state = board_state.copy()
        self.parent = parent
        self.move = move  # (from_pos, to_pos)
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = []
        self.player_id = player_id

class MCTSAI:
    def __init__(self, player_id, time_limit=1.0):
        """
        :param player_id: 玩家ID
        :param time_limit: 单次决策的时间限制（秒），如 1.0 表示 1 秒
        """
        self.player_id = player_id
        self.time_limit = time_limit

    def choose_move(self, board):
        # 创建根节点
        root = MCTSNode(board, self.player_id)
        root.untried_moves = get_all_moves(board, self.player_id)
        if not root.untried_moves:
            return None

        start_time = time.time()
        iteration_count = 0

        # 在剩余时间内不断进行 MCTS 搜索
        while True:
            if time.time() - start_time > self.time_limit:
                break
            iteration_count += 1

            node = self.select(root)
            if node.untried_moves:
                node = self.expand(node)
            result = self.simulate(node)
            self.backpropagate(node, result)

        # 从根节点的子节点中选访问次数最多的
        if not root.children:
            return random.choice(root.untried_moves) if root.untried_moves else None
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move if best_child.move else None

    def select(self, node):
        # 当无未试走法且有子节点，采用 best_child 往下走
        while not node.untried_moves and node.children:
            node = self.best_child(node)
        return node

    def best_child(self, node):
        C = 1.4
        return max(
            node.children,
            key=lambda c: (c.wins / c.visits) + C * math.sqrt(math.log(node.visits) / c.visits)
        )

    def expand(self, node):
        move = node.untried_moves.pop()
        new_board = node.board_state.copy()
        f, t = move
        if new_board[t] == 0:
            new_board[t] = new_board[f]
            new_board[f] = 0
        child_node = MCTSNode(new_board, self.player_id, parent=node, move=move)
        child_node.untried_moves = get_all_moves(new_board, self.player_id)
        node.children.append(child_node)
        return child_node

    def simulate(self, node):
        # 半贪心模拟：自己回合选择最佳走法，其它玩家随机
        board = node.board_state.copy()
        current_player = self.player_id
        depth_limit = 15  # 降低模拟步数

        for _ in range(depth_limit):
            moves = get_all_moves(board, current_player)
            if not moves:
                break

            if current_player == self.player_id:
                # 在自己回合采用简单贪心：选 evaluation 最佳
                best_move = None
                best_val = -float('inf')
                for m in moves:
                    sim_board = board.copy()
                    ff, tt = m
                    sim_board[tt] = sim_board[ff]
                    sim_board[ff] = 0
                    val = self.evaluate(sim_board)
                    if val > best_val:
                        best_val = val
                        best_move = m
                chosen_move = best_move if best_move else random.choice(moves)
            else:
                # 其余玩家随机
                chosen_move = random.choice(moves)

            f, t = chosen_move
            board[t] = board[f]
            board[f] = 0
            current_player = (current_player % 4) + 1

        return self.evaluate(board)

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result > 0:
                node.wins += 1
            node = node.parent

    def evaluate(self, board):
        # 简单评价：己方棋子到目标角的曼哈顿距离之和 (越小越好 => return -distance_sum)
        if self.player_id == 1:
            target = (11, 11)
        elif self.player_id == 2:
            target = (11, 0)
        elif self.player_id == 3:
            target = (0, 11)
        elif self.player_id == 4:
            target = (0, 0)
        positions = np.argwhere(board == self.player_id)
        total_dist = sum(abs(p[0] - target[0]) + abs(p[1] - target[1]) for p in positions)
        return -total_dist
