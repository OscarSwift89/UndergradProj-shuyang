# ai/move_utils.py
import numpy as np

def get_valid_moves(pos, board):
    x, y = pos
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1] and board[nx, ny] == 0:
            moves.append((nx, ny))
    return moves

def get_jump_moves(pos, board):
    x, y = pos
    moves = []
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for dx, dy in directions:
        midx, midy = x + dx, y + dy
        landingx, landingy = x + 2 * dx, y + 2 * dy
        if (0 <= midx < board.shape[0] and 0 <= midy < board.shape[1] and board[midx, midy] != 0):
            if (0 <= landingx < board.shape[0] and 0 <= landingy < board.shape[1] and board[landingx, landingy] == 0):
                moves.append((landingx, landingy))
    return moves

def get_all_moves(board, player_id, as_move_tuple=True):
    moves = []
    positions = np.argwhere(board == player_id)
    for pos in positions:
        pos = tuple(pos)
        valid = get_valid_moves(pos, board)
        jump = get_jump_moves(pos, board)
        if as_move_tuple:
            moves.extend([(pos, m) for m in valid])
            moves.extend([(pos, m) for m in jump])
        else:
            moves.extend(valid)
            moves.extend(jump)
    return moves


def get_continuous_jump_moves(pos, board, visited=None, max_depth=3):
    """
    实现连续跳跃（包括相邻跳与等距跳）的搜索，增加了一个 max_depth 限制连续跳跃的最大次数，
    避免无限递归或生成过多候选走法。
    参数:
      pos: 当前起始位置
      board: 棋盘（numpy 数组）
      visited: 记录已访问位置的集合，用以防止循环
      max_depth: 最大连续跳跃深度，达到后不再递归
    返回:
      一个列表，每个元素是一个路径（列表形式），路径的第一个元素为起点，最后一个元素为落点。
    """
    if visited is None:
        visited = set([pos])
    if max_depth <= 0:
        return []
    paths = []
    # 只考虑上下左右四个方向（如需扩展可加入对角方向）
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for d in directions:
        L = 2
        while True:
            new_r = pos[0] + L * d[0]
            new_c = pos[1] + L * d[1]
            if not (0 <= new_r < board.shape[0] and 0 <= new_c < board.shape[1]):
                break
            target = (new_r, new_c)
            mid = (pos[0] + (L // 2) * d[0], pos[1] + (L // 2) * d[1])
            # 条件：目标为空，且中间位置有棋子（无论哪一方）
            if board[target] == 0 and board[mid] != 0:
                if target not in visited:
                    new_path = [pos, target]
                    paths.append(new_path)
                    new_visited = set(visited)
                    new_visited.add(target)
                    further_paths = get_continuous_jump_moves(target, board, new_visited, max_depth-1)
                    for fp in further_paths:
                        # 拼接路径：fp[0]通常为target，因此只添加 fp[1:]
                        paths.append([pos] + fp[1:])
            L += 2
    return paths
     
    

def free_up_target_entry(board, player_id):
    """
    当目标区域被几乎填满时，导致剩余一两个棋子无法移动进入目标区域，
    尝试在目标区域腾出外部位置，使得外面棋子可以移动进入
    """
    # 玩家1情况
    if player_id == 1: 
        for row in range(9, 12):
            for col in range(9, 12):
                if board[row, col] == 1:
                    # 如果当前棋子刚好在目标入口边界（行跟列刚好是9）
                    if row == 9 or col == 9:
                        candidates = []
                        # 尝试向内部移动
                        if row + 1 < 12 and board[row + 1, col] == 0:
                            candidates.append((row + 1, col))
                        if col + 1 < 12 and board[row, col + 1] == 0:
                            candidates.append((row, col + 1))
                        if row + 1 < 12 and col + 1 < 12 and board[row + 1, col + 1] == 0:
                            candidates.append((row + 1, col + 1))
                        if candidates:
                            # 返回深层目标（区域内）最近的候选位置
                            best_candidate = min(candidates, key=lambda pos: abs(pos[0] - 11) + abs(pos[1] - 11))
                            return ((row, col), best_candidate)
        return None
    else:
        # 玩家2情况
        for row in range(0, 3):
            for col in range(0, 3):
                if board[row, col] == 2:
                    if row == 2 or col == 2:
                        candidates = []
                        if row - 1 >= 0 and board[row - 1, col] == 0:
                            candidates.append((row - 1, col))
                        if col - 1 >= 0 and board[row, col - 1] == 0:
                            candidates.append((row, col - 1))
                        if row - 1 >= 0 and col - 1 >= 0 and board[row - 1, col - 1] == 0:
                            candidates.append((row - 1, col - 1))
                        if candidates:
                            best_candidate = min(candidates, key=lambda pos: abs(pos[0] - 0) + abs(pos[1] - 0))
                            return ((row, col), best_candidate)
        return None
    #可以再添加其他玩家棋子的判断逻辑                