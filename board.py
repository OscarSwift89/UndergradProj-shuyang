import numpy as np
from colorama import Fore, Style

class Board:
    def __init__(self):
        # 初始化12x12棋盘
        self.board = np.zeros((12, 12), dtype=int)
        self.init_pieces()

    def init_pieces(self):
        """
        根据 GUI 的区域设置，将初始棋子分配如下：
          - 左上区域 (i < 3, j < 3)：玩家4（skyblue 区域）
          - 右上区域 (i < 3, j >= 9)：玩家3（lightgreen 区域）
          - 左下区域 (i >= 9, j < 3)：玩家2（khaki 区域）
          - 右下区域 (i >= 9, j >= 9)：玩家1（lightcoral 区域）
        """
        # 玩家4：左上区域
        self.board[0:3, 0:3] = 4

        # 玩家3：右上区域
        self.board[0:3, 9:12] = 3

        # 玩家2：左下区域
        self.board[9:12, 0:3] = 2

        # 玩家1：右下区域
        self.board[9:12, 9:12] = 1

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
                      (1, -1),  (1, 0),  (1, 1)]
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2 * dx , y + 2 * dy
            if 0 <= midx < 12 and 0 <= midy < 12 and self.board[midx, midy]:
                if 0 <= landingx < 12 and 0 <= landingy < 12 and self.board[landingx, landingy] == 0:
                    jumps.append((landingx, landingy))
        return jumps

    def is_game_over(self):
        """胜利条件：这里仅提供简单示例，可根据实际调整"""
        if np.count_nonzero(self.board[9:12, 9:12] == 1) == 9:
            return True
        if np.count_nonzero(self.board[9:12, 0:3] == 2) == 9:
            return True
        if np.count_nonzero(self.board[0:3, 9:12] == 3) == 9:
            return True
        if np.count_nonzero(self.board[0:3, 0:3] == 4) == 9:
            return True
        return False

    def render(self):
        """彩色渲染棋盘至终端"""
        symbols = {
            0: Fore.WHITE + '.' + Style.RESET_ALL,  # 空位：白色
            1: Fore.RED + '●' + Style.RESET_ALL,      # 玩家1：红色
            2: Fore.BLUE + '●' + Style.RESET_ALL,     # 玩家2：蓝色
            3: Fore.GREEN + '●' + Style.RESET_ALL,     # 玩家3：绿色
            4: Fore.MAGENTA + '●' + Style.RESET_ALL    # 玩家4：品红色
        }
        print("\n当前棋盘状态：")
        for row in self.board:
            print(' '.join([symbols[cell] for cell in row]))
        print("\n" + "=" * 33 + "\n")
