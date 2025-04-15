import numpy as np
from colorama import Fore, Style

class Board:
    def __init__(self):
        # 初始化 12x12 棋盘，全为 0 表示空位
        self.board = np.zeros((12, 12), dtype=int)
        self.init_pieces()

    def init_pieces(self):
        """
        四人中国跳棋起始布局：  
          - 玩家1起始区域：左上角（board[0:3, 0:3]），目标区域：右下角  
          - 玩家2起始区域：右上角（board[0:3, 9:12]），目标区域：左下角  
          - 玩家3起始区域：左下角（board[9:12, 0:3]），目标区域：右上角  
          - 玩家4起始区域：右下角（board[9:12, 9:12]），目标区域：左上角
        """
        # 玩家1的棋子（编号1）放在左上角
        self.board[0:3, 0:3] = 1
        # 玩家2的棋子（编号2）放在右上角
        self.board[0:3, 9:12] = 2
        # 玩家3的棋子（编号3）放在左下角
        self.board[9:12, 0:3] = 3
        # 玩家4的棋子（编号4）放在右下角
        self.board[9:12, 9:12] = 4

    def move_piece(self, from_pos, to_pos):
        """移动棋子，如果目标位置为空则移动成功"""
        if self.board[to_pos] == 0:
            self.board[to_pos] = self.board[from_pos]
            self.board[from_pos] = 0
            return True
        return False

    def get_valid_moves(self, pos):
        """获取指定位置的所有基本（上下左右）合法移动"""
        x, y = pos
        moves = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12 and self.board[nx, ny] == 0:
                moves.append((nx, ny))
        return moves

    def get_jump_moves(self, pos):
        """获取指定位置的所有跳跃移动（检查8个方向）"""
        x, y = pos
        jumps = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2*dx, y + 2*dy
            if (0 <= midx < 12 and 0 <= midy < 12 and self.board[midx, midy] != 0 and
                0 <= landingx < 12 and 0 <= landingy < 12 and self.board[landingx, landingy] == 0):
                jumps.append((landingx, landingy))
        return jumps

    def is_game_over(self):
        """
        胜利条件示例：  
        当某一玩家的目标区域（按 main.py 分数统计区域）被填满时（例如9个棋子），返回 True  
        注意：实际游戏中胜利条件可更复杂。
        """
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
            0: Fore.WHITE + '.' + Style.RESET_ALL,
            1: Fore.RED + '●' + Style.RESET_ALL,
            2: Fore.BLUE + '●' + Style.RESET_ALL,
            3: Fore.GREEN + '●' + Style.RESET_ALL,
            4: Fore.MAGENTA + '●' + Style.RESET_ALL
        }
        print("\n当前棋盘状态：")
        for row in self.board:
            print(' '.join([symbols[cell] for cell in row]))
        print("\n" + "=" * 33 + "\n")
