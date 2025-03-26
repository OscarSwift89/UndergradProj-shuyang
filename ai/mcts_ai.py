import random
import math
import numpy as np
from board import Board

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
        root.untried_moves = self.get_all_moves(board)
        if not root.untried_moves:
            return None  # 无合法移动
        
        for _ in range(self.iterations):
            node = self.select(root)
            # 如果节点还有未尝试的移动，则扩展
            if node.untried_moves:
                node = self.expand(node)
            result = self.simulate(node)
            self.backpropagate(node, result)
            
        # 如果没有生成任何子节点，返回随机合法移动作为备用
        if not root.children:
            return random.choice(root.untried_moves) if root.untried_moves else None
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move if best_child.move else None

    def get_all_moves(self, board):
        moves = []
        # board 为 numpy 数组，获取所有当前玩家的棋子位置
        positions = np.argwhere(board == self.player_id)
        for pos in positions:
            pos = tuple(pos)
            moves.extend(self.get_valid_moves(pos, board))
            moves.extend(self.get_jump_moves(pos, board))
        return moves
    
    def get_valid_moves(self, pos, board):
        x, y = pos
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 17 and 0 <= ny < 17 and board[nx, ny] == 0:
                moves.append((pos, (nx, ny)))
        return moves
    
    def get_jump_moves(self, pos, board):
        x, y = pos
        jumps = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2 * dx, y + 2 * dy
            if 0 <= midx < 17 and 0 <= midy < 17 and board[midx, midy] != 0:
                if 0 <= landingx < 17 and 0 <= landingy < 17 and board[landingx, landingy] == 0:
                    jumps.append((pos, (landingx, landingy)))
        return jumps

    def select(self, node):
        # 选择阶段：如果当前节点没有未尝试的移动且有子节点，则选择最佳子节点
        while not node.untried_moves and node.children:
            node = self.best_child(node)
        return node
    
    def best_child(self, node):
        C = 1.4  # 探索系数
        return max(node.children, key=lambda c: c.wins / c.visits + C * math.sqrt(math.log(node.visits) / c.visits))
    
    def expand(self, node):
        move = node.untried_moves.pop()
        new_board = node.board_state.copy()
        # 执行移动：移动棋子 (from_pos -> to_pos)
        from_pos, to_pos = move
        if new_board[to_pos] == 0:
            new_board[to_pos] = new_board[from_pos]
            new_board[from_pos] = 0
        child_node = MCTSNode(new_board, self.player_id, parent=node, move=move)
        child_node.untried_moves = self.get_all_moves(new_board)
        node.children.append(child_node)
        return child_node
    
    def simulate(self, node):
        # 简单的随机模拟：直接随机返回 0 或 1 作为结果
        # 真实应用中应从当前状态随机走到终局
        return random.choice([0, 1])
    
    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result == self.player_id:
                node.wins += 1
            node = node.parent
