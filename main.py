import tkinter as tk
from tkinter import ttk
from game import Game

import time
import psutil
import os

#导入ai代理模块
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI
#from ai.bfs_ai import BFSAI

# 定义一个简单的 GUI 游戏类，用画布显示棋盘
class GameGUI:
    def __init__(self, root, p1_ai, p2_ai):
        self.root = root
        # 主框架分为左右两部分：左侧棋盘，右侧信息面板
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=600, height=600)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        self.info_label = tk.Label(self.info_frame, text="Algorithm Info", justify=tk.LEFT)
        self.info_label.pack()

        self.game = Game(p1_ai, p2_ai)
        # 棋盘尺寸为15×17，单元格大小调整为600//17
        self.cell_size = 600 // 17
        self.update_board()

        self.root.after(1000, self.game_step)

    def update_info(self, ai_name, elapsed_time, memory_usage):
        info_text = f"当前AI: {ai_name}\n"
        info_text += f"上次计算时间: {elapsed_time:.4f} 秒\n"
        info_text += f"当前内存使用: {memory_usage:.2f} MB"
        self.info_label.config(text=info_text)

    def update_board(self):
        self.canvas.delete("all")
        board = self.game.board.board
        for i in range(17):
            for j in range(17):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                if board[i, j] == 1:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="red")
                elif board[i, j] == 2:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="blue")

    def game_step(self):
        if not self.game.board.is_game_over():
            current_ai = self.game.players[self.game.current_player]
            start_time = time.time()
            move = current_ai.choose_move(self.game.board.board)
            elapsed = time.time() - start_time
            # 获取当前进程内存使用（以 MB 为单位）
            process = psutil.Process(os.getpid())
            mem = process.memory_info().rss / (1024 * 1024)
            ai_name = type(current_ai).__name__
            self.update_info(ai_name, elapsed, mem)

            if move:
                from_pos, to_pos = move
                self.game.board.move_piece(from_pos, to_pos)
            self.game.current_player = 2 if self.game.current_player == 1 else 1
            self.update_board()
            self.root.after(1000, self.game_step)
        else:
            self.info_label.config(text="游戏结束！")

def start_game(p1_type, p2_type, root, selection_frame):
    def create_ai(ai_type, player_id):
        if ai_type == "Greedy":
            return GreedyAI(player_id)
        elif ai_type == "A* 算法":
            return AStarAI(player_id)
        elif ai_type == "MCTS":
            return MCTSAI(player_id)
        elif ai_type == "Minimax":
            return MinimaxAI(player_id)
        #elif ai_type == "BFS":
        #    return BFSAI(player_id)
        else:
            return GreedyAI(player_id)
    p1_ai = create_ai(p1_type, 1)
    p2_ai = create_ai(p2_type, 2)
    selection_frame.destroy()
    GameGUI(root, p1_ai, p2_ai)

root = tk.Tk()
root.title("中国跳棋AI对战")
selection_frame = tk.Frame(root)
selection_frame.pack(padx=10, pady=10)
# 5个算法选项，包含新增的 A*、Minimax、BFS
options = ["Greedy", "A* 算法", "MCTS", "Minimax", "BFS"]

tk.Label(selection_frame, text="选择玩家1的AI:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家2的AI:").grid(row=1, column=0, padx=5, pady=5)
p1_var = tk.StringVar(value="Greedy")
p2_var = tk.StringVar(value="Greedy")
p1_menu = ttk.Combobox(selection_frame, textvariable=p1_var, values=options, state="readonly")
p1_menu.grid(row=0, column=1, padx=5, pady=5)
p2_menu = ttk.Combobox(selection_frame, textvariable=p2_var, values=options, state="readonly")
p2_menu.grid(row=1, column=1, padx=5, pady=5)

start_button = tk.Button(selection_frame, text="开始游戏", 
                         command=lambda: start_game(p1_var.get(), p2_var.get(), root, selection_frame))
start_button.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()