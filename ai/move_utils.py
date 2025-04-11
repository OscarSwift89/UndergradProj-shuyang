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
