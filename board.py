import numpy as np
from colorama import Fore, Back, Style

class Board:
    def __init__(self):
        # 初始化12x12棋盘
        self.board = np.zeros((12, 12), dtype=int)
        self.init_pieces()

    def init_pieces(self):
        # 玩家1的初始位置（左上角区域）
        self.board[0:3, 0:3] = 1
        # 玩家2的初始位置（右下角区域）
        self.board[-3:, -3:] = 2

    def move_piece(self, from_pos, to_pos):
        """移动棋子并返回是否成功"""
        if self.board[to_pos] == 0:
            self.board[to_pos] = self.board[from_pos]
            self.board[from_pos] = 0
            return True
        return False

    def get_valid_moves(self, pos):
        """获取指定位置的所有合法移动"""
        x, y = pos
        moves = []
        # 基础移动：上下左右
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12:
                if self.board[nx, ny] == 0:
                    moves.append((nx, ny))
        return moves

    def get_jump_moves(self, pos):
        """获取所有跳跃移动（检查八个方向）"""
        x, y = pos
        jumps = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]  #上下左右等八个方向
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2 * dx , y + 2 * dy
            if 0 <= midx < 12 and 0 <= midy < 12 and self.board[midx, midy]:
                if 0 <= landingx < 12 and 0 <= landingy < 12 and self.board[landingx, landingy]:
                    jumps.append((landingx, landingy))
        return jumps


    def is_game_over(self):
        """胜利条件：当玩家1的所有棋子均移动到右下区域，
           或玩家2的所有棋子均移动到左上区域时，游戏结束。"""
        # 假设每个玩家初始有16个棋子（4x4区域）
        if np.count_nonzero(self.board[-3:, -3:] == 1) == 9:
            return True
        if np.count_nonzero(self.board[0:3, 0:3] == 2) == 9:
            return True
        return False


    def render(self):
        """彩色渲染棋盘"""
        symbols = {
            0: Fore.WHITE + '.' + Style.RESET_ALL,  # 空位：白色
            1: Fore.RED + '●' + Style.RESET_ALL,    # 玩家1：红色
            2: Fore.BLUE + '●' + Style.RESET_ALL    # 玩家2：蓝色
        }
        print("\n当前棋盘状态：")
        for row in self.board:
            print(' '.join([symbols[cell] for cell in row]))
        print("\n" + "=" * 33 + "\n")