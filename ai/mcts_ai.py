# ai/mcts_ai.py
import random
import math
import numpy as np
from .move_utils import get_all_moves

"""改进后的 MCTS 算法：
   新的随机模拟阶段（simulate）不再简单随机返回，而是进行有限步随机走子后，
   根据局面评估函数返回胜负判定，从而更好地引导搜索。
"""
class MCTSNode:
    def __init__(self, board_state, player_id, parent=None, move=None):
        self.board_state = board_state.copy()
        self.parent = parent
        self.move = move  # (from_pos, to_pos) 使该节点产生的移动
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = []  # 初始化为空列表
        self.player_id = player_id

class MCTSAI:
    def __init__(self, player_id, iterations=100):
        self.player_id = player_id
        self.iterations = iterations
        
    def choose_move(self, board):
        # 创建根节点，并初始化所有合法移动
        root = MCTSNode(board, self.player_id)
        root.untried_moves = get_all_moves(board, self.player_id)
        if not root.untried_moves:
            return None  # 无合法移动
        
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
        while not node.untried_moves and node.children:
            node = self.best_child(node)
        return node
    
    def best_child(self, node):
        C = 1.4
        return max(node.children, key=lambda c: c.wins / c.visits + C * math.sqrt(math.log(node.visits) / c.visits))
    
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
        """
        新的随机模拟：从 node.board_state 出发，双方交替进行随机走子，
        进行固定步数（例如 10 步）或提前终止后，根据局面评估函数返回胜利方。
        """
        board = node.board_state.copy()
        current_player = self.player_id
        depth_limit = 10
        for _ in range(depth_limit):
            moves = get_all_moves(board, current_player)
            if not moves:
                break
            move = random.choice(moves)
            from_pos, to_pos = move
            # 执行移动
            board[to_pos] = board[from_pos]
            board[from_pos] = 0
            # 交替走子
            current_player = 2 if current_player == 1 else 1
        
        # 评估局面：利用己方与对手棋子距离各自目标区域的曼哈顿距离差值
        eval_val = self.evaluate(board)
        # 如果 eval_val > 0，认为局面对 self.player_id 有利，返回 self.player_id；否则返回对手编号
        return self.player_id if eval_val > 0 else (2 if self.player_id == 1 else 1)
    
    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result == self.player_id:
                node.wins += 1
            node = node.parent

    def evaluate(self, board):
        """
        局面评估函数：
         - 对于玩家1，目标为棋盘右下角 (11, 11)；对于玩家2，目标为 (0, 0)。
         - 计算所有己方棋子到目标的曼哈顿距离总和，以及对手棋子的总和，
           返回 (对手距离和 - 己方距离和) 。
         数值越大表示己方优势越明显。
        """
        if self.player_id == 1:
            my_target = (11, 11)
            opp_target = (0, 0)
        else:
            my_target = (0, 0)
            opp_target = (11, 11)
        my_positions = np.argwhere(board == self.player_id)
        opp_positions = np.argwhere(board == (2 if self.player_id == 1 else 1))
        my_distance = sum([abs(pos[0] - my_target[0]) + abs(pos[1] - my_target[1]) for pos in my_positions])
        opp_distance = sum([abs(pos[0] - opp_target[0]) + abs(pos[1] - opp_target[1]) for pos in opp_positions])
        return opp_distance - my_distance

