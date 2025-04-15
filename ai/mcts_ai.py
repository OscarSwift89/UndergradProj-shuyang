# ai/mcts_ai.py
import random
import math
import numpy as np
from .move_utils import get_all_moves


#需要修改
class MCTSNode:
    def __init__(self, board_state, player_id, parent=None, move=None):
        self.board_state = board_state.copy()
        self.parent = parent
        self.move = move  # 该节点产生的移动
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = []
        self.player_id = player_id

class MCTSAI:
    def __init__(self, player_id, iterations=100):
        self.player_id = player_id
        self.iterations = iterations
        
    def choose_move(self, board):
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
        while not node.untried_moves and node.children:
            node = self.best_child(node)
        return node
    
    def best_child(self, node):
        C = 1.4
        return max(node.children, key=lambda c: (c.wins / c.visits) + C * math.sqrt(math.log(node.visits) / c.visits))
    
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
        depth_limit = 10
        for _ in range(depth_limit):
            moves = get_all_moves(board, current_player)
            if not moves:
                break
            move = random.choice(moves)
            from_pos, to_pos = move
            board[to_pos] = board[from_pos]
            board[from_pos] = 0
            current_player = (current_player % 4) + 1  # 轮换4个玩家
        return self.evaluate(board)
    
    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            # 简单的：result > 0 则认为有利于 self.player_id
            if result > 0:
                node.wins += 1
            node = node.parent

    def evaluate(self, board):
        if self.player_id == 1:
            my_target = (11, 11)
        elif self.player_id == 2:
            my_target = (11, 0)
        elif self.player_id == 3:
            my_target = (0, 11)
        elif self.player_id == 4:
            my_target = (0, 0)
        my_positions = np.argwhere(board == self.player_id)
        my_distance = sum([abs(pos[0] - my_target[0]) + abs(pos[1] - my_target[1]) for pos in my_positions])
        return -my_distance
