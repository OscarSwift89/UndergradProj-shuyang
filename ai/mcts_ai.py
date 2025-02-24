import random
import math
import numpy as np  # 添加这一行

class MCTSNode:
    def __init__(self, board_state, parent=None, move=None):
        self.board_state = board_state.copy()
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = None

class MCTSAI:
    def __init__(self, player_id, iterations=100):
        self.player_id = player_id
        self.iterations = iterations
        
    def choose_move(self, board):
        root = MCTSNode(board)
        
        for _ in range(self.iterations):
            node = self.select(root)
            result = self.simulate(node)
            self.backpropagate(node, result)
            
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move if best_child else None
    
    def select(self, node):
        while node.untried_moves is None or not node.untried_moves:
            if not node.children:
                return node
            node = self.best_child(node)
        return node
    
    def best_child(self, node):
        C = 1.4  # 探索系数
        return max(node.children, 
                   key=lambda c: c.wins/c.visits + C * math.sqrt(math.log(node.visits)/c.visits))
    
    def expand(self, node):
        move = node.untried_moves.pop()
        new_board = node.board_state.copy()
        # 需要实现实际移动逻辑
        child_node = MCTSNode(new_board, parent=node, move=move)
        node.children.append(child_node)
        return child_node
    
    def simulate(self, node):
        # 简化随机模拟
        return random.choice([0, 1])
    
    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result == self.player_id:
                node.wins += 1
            node = node.parent