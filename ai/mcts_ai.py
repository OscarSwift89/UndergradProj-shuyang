# ai/mcts_ai.py
import random
import math
import numpy as np
from .move_utils import get_all_moves

class MCTSNode:
    def __init__(self, board_state, player_id, parent=None, move=None):
        self.board_state = board_state.copy()
        self.parent = parent
        self.move = move  # 使该节点产生的移动，格式为 (from_pos, to_pos)
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = []
        self.player_id = player_id

class MCTSAI:
    def __init__(self, player_id, iterations=2000):
        self.player_id = player_id
        self.iterations = iterations

    def choose_move(self, board):
        # 创建根节点，扩展所有己方合法走法
        root = MCTSNode(board, self.player_id)
        root.untried_moves = get_all_moves(board, self.player_id)
        if not root.untried_moves:
            return None

        for _ in range(self.iterations):
            node = self.select(root)
            if node.untried_moves:
                node = self.expand(node)
            result = self.simulate(node)
            self.backpropagate(node, result)
            
        if not root.children:
            return random.choice(root.untried_moves) if root.untried_moves else None
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move if best_child.move else None

    def select(self, node):
        # 选择策略：当当前节点无未试走法时，从子节点中选择具有最高 UCT 值的节点
        while not node.untried_moves and node.children:
            node = self.best_child(node)
        return node

    def best_child(self, node):
        C = 1.4  # 常数参数
        return max(
            node.children, 
            key=lambda c: (c.wins / c.visits) + C * math.sqrt(math.log(node.visits) / c.visits)
        )

    def expand(self, node):
        move = node.untried_moves.pop()
        new_board = node.board_state.copy()
        from_pos, to_pos = move
        if new_board[to_pos] == 0:
            new_board[to_pos] = new_board[from_pos]
            new_board[from_pos] = 0
        child_node = MCTSNode(new_board, self.player_id, parent=node, move=move)
        child_node.untried_moves = get_all_moves(new_board, self.player_id)
        node.children.append(child_node)
        return child_node

    def simulate(self, node):
        board = node.board_state.copy()
        current_player = self.player_id
        depth_limit = 50  # 增加模拟深度
        for _ in range(depth_limit):
            moves = get_all_moves(board, current_player)
            if not moves:
                break
            if current_player == self.player_id:
                # 当轮到己方时，使用简单的贪心策略选择走法
                best_move = None
                best_value = -float('inf')
                for move in moves:
                    sim_board = board.copy()
                    from_pos, to_pos = move
                    sim_board[to_pos] = sim_board[from_pos]
                    sim_board[from_pos] = 0
                    value = self.evaluate(sim_board)
                    if value > best_value:
                        best_value = value
                        best_move = move
                chosen_move = best_move if best_move is not None else random.choice(moves)
            else:
                # 对于其他玩家，随机选择走法
                chosen_move = random.choice(moves)
            from_pos, to_pos = chosen_move
            board[to_pos] = board[from_pos]
            board[from_pos] = 0
            current_player = (current_player % 4) + 1
        return self.evaluate(board)

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            # 简单起见，若评价值为正，则认为局面对己方有利
            if result > 0:
                node.wins += 1
            node = node.parent

    def evaluate(self, board):
        # 根据己方棋子距离目标区域的曼哈顿距离求和（距离越短越好）
        if self.player_id == 1:
            target = (11, 11)   # 玩家1目标：右下角
        elif self.player_id == 2:
            target = (11, 0)    # 玩家2目标：左下角
        elif self.player_id == 3:
            target = (0, 11)    # 玩家3目标：右上角
        elif self.player_id == 4:
            target = (0, 0)     # 玩家4目标：左上角
        positions = np.argwhere(board == self.player_id)
        total_distance = sum(abs(pos[0] - target[0]) + abs(pos[1] - target[1]) for pos in positions)
        # 返回负值，距离越短（即更接近目标）则评价越高
        return -total_distance
