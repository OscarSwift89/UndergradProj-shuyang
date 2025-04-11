import tkinter as tk
from tkinter import ttk, messagebox
import time
import tracemalloc
import psutil
import os
import numpy as np

from game import Game
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI

class GameGUI:
    def __init__(self, root, p1_ai, p2_ai, game_duration):
        self.root = root
        self.game_duration = game_duration  # 游戏总时长（秒）
        
        # 使用 grid 布局，棋盘在左，信息面板在右
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        self.info_frame = tk.Frame(root)
        self.info_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)
        self.create_info_panel()
        
        self.game = Game(p1_ai, p2_ai)
        self.cell_size = 600 // 12
        
        # 记录各玩家决策耗时、累计耗时、决策次数、最新决策内存（字节）
        self.stats = {
            1: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0},
            2: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0}
        }
        self.start_time = time.perf_counter()
        self.process = psutil.Process(os.getpid())
        
        self.update_board()
        self.root.after(1000, self.game_step)

    def create_info_panel(self):
        # 分别为玩家1和玩家2建立信息区域
        self.info_labels = {}
        for player in [1, 2]:
            frame = tk.LabelFrame(self.info_frame, text=f"玩家 {player} 信息", padx=5, pady=5)
            frame.pack(fill="x", pady=5)
            self.info_labels[player] = {}
            self.info_labels[player]['current_time'] = tk.Label(frame, text="当前决策耗时: -")
            self.info_labels[player]['current_time'].pack(anchor="w")
            self.info_labels[player]['cumulative_time'] = tk.Label(frame, text="累计决策耗时: -")
            self.info_labels[player]['cumulative_time'].pack(anchor="w")
            self.info_labels[player]['decision_count'] = tk.Label(frame, text="决策次数: -")
            self.info_labels[player]['decision_count'].pack(anchor="w")
            self.info_labels[player]['latest_mem'] = tk.Label(frame, text="最新决策内存: -")
            self.info_labels[player]['latest_mem'].pack(anchor="w")
        
        # 总内存消耗和游戏运行时间
        self.total_mem_label = tk.Label(self.info_frame, text="总内存消耗: -")
        self.total_mem_label.pack(anchor="w", pady=(10,0))
        self.elapsed_label = tk.Label(self.info_frame, text="游戏运行时间: -")
        self.elapsed_label.pack(anchor="w", pady=(0,10))
        # 分数统计标签
        self.score_label = tk.Label(self.info_frame, text="分数 - 玩家1: 0, 玩家2: 0", font=("Arial", 12, "bold"))
        self.score_label.pack(anchor="w", pady=(10,0))

    def update_info_panel(self, elapsed, total_mem):
        for player in [1, 2]:
            cur = self.stats[player]
            self.info_labels[player]['current_time'].config(text=f"当前决策耗时: {cur['decision_time']*1000:.1f} ms")
            self.info_labels[player]['cumulative_time'].config(text=f"累计决策耗时: {cur['cumulative_time']:.2f} s")
            self.info_labels[player]['decision_count'].config(text=f"决策次数: {cur['decision_count']}")
            self.info_labels[player]['latest_mem'].config(text=f"最新决策内存: {cur['latest_mem'] / 1024:.1f} KB")
        self.total_mem_label.config(text=f"总内存消耗: {total_mem / (1024*1024):.1f} MB")
        self.elapsed_label.config(text=f"游戏运行时间: {elapsed:.1f} s")
        
        # 更新分数：玩家1得分为棋盘下右角的玩家1棋子数，玩家2得分为棋盘上左角的玩家2棋子数
        board = self.game.board.board
        p1_score = np.count_nonzero(board[9:12,9:12] == 1) ############
        p2_score = np.count_nonzero(board[0:3,0:3] == 2)     ############
        self.score_label.config(text=f"分数 - 玩家1: {p1_score}, 玩家2: {p2_score}")

    def update_board(self):
        self.canvas.delete("all")
        board = self.game.board.board
        for i in range(12):
            for j in range(12):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                # 为四个角区域设定特殊背景色
                if 0 <= i < 3 and 0 <= j < 3:
                    fill_color = "skyblue"       # 上左角：玩家2目标区域
                elif 0 <= i < 3 and 9 <= j < 12:
                    fill_color = "lightgreen"    # 上右角：中性
                elif 9 <= i < 12 and 0 <= j < 3:
                    fill_color = "khaki"         # 下左角：中性
                elif 9 <= i < 12 and 9 <= j < 12:
                    fill_color = "lightcoral"    # 下右角：玩家1目标区域
                else:
                    fill_color = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                
                # 绘制棋子
                if board[i, j] == 1:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="red")
                elif board[i, j] == 2:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="blue")
    
    def game_step(self):
        elapsed = time.perf_counter() - self.start_time
        total_mem = self.process.memory_info().rss
        
        # 检查是否达到规定时间，若达到则结束游戏并统计分数
        if elapsed >= self.game_duration:
            board = self.game.board.board
            p1_score = np.count_nonzero(board[9:12,9:12] == 1)
            p2_score = np.count_nonzero(board[0:3,0:3] == 2)
            if p1_score > p2_score:
                winner = "玩家1"
            elif p2_score > p1_score:
                winner = "玩家2"
            else:
                winner = "平局"
            # 在棋盘中央显示胜利信息
            self.canvas.create_text(300, 300, text=f"{winner}胜利", font=("Arial", 36, "bold"), fill="purple")
            return
        
        current_player = self.game.current_player
        current_ai = self.game.players[current_player]
        
        # 记录决策前后时间与内存
        tracemalloc.start()
        start_decision = time.perf_counter()
        move = current_ai.choose_move(self.game.board.board)
        decision_time = time.perf_counter() - start_decision
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.stats[current_player]['decision_time'] = decision_time
        self.stats[current_player]['cumulative_time'] += decision_time
        self.stats[current_player]['decision_count'] += 1
        self.stats[current_player]['latest_mem'] = peak_mem
        
        if move:
            from_pos, to_pos = move
            self.game.board.move_piece(from_pos, to_pos)
        
        self.game.current_player = 2 if current_player == 1 else 1
        
        self.update_board()
        self.update_info_panel(elapsed, total_mem)
        self.root.after(1000, self.game_step)

def start_game(p1_type, p2_type, game_duration, root, selection_frame):
    def create_ai(ai_type, player_id):
        if ai_type == "Greedy":
            return GreedyAI(player_id)
        elif ai_type == "A* 算法":
            return AStarAI(player_id)
        elif ai_type == "MCTS":
            return MCTSAI(player_id)
        elif ai_type == "Minimax":
            return MinimaxAI(player_id)
        else:
            return GreedyAI(player_id)
        
    p1_ai = create_ai(p1_type, 1)
    p2_ai = create_ai(p2_type, 2)
    selection_frame.destroy()
    GameGUI(root, p1_ai, p2_ai, game_duration)

root = tk.Tk()
root.title("中国跳棋AI对战")
selection_frame = tk.Frame(root)
selection_frame.pack(padx=10, pady=10)

options = ["Greedy", "A* 算法", "MCTS", "Minimax", "BFS"]

tk.Label(selection_frame, text="选择玩家1的AI:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家2的AI:").grid(row=1, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择游戏时长:").grid(row=2, column=0, padx=5, pady=5)

p1_var = tk.StringVar(value="Greedy")
p2_var = tk.StringVar(value="Greedy")
time_var = tk.StringVar(value="1分钟")  # 默认1分钟

p1_menu = ttk.Combobox(selection_frame, textvariable=p1_var, values=options, state="readonly")
p1_menu.grid(row=0, column=1, padx=5, pady=5)
p2_menu = ttk.Combobox(selection_frame, textvariable=p2_var, values=options, state="readonly")
p2_menu.grid(row=1, column=1, padx=5, pady=5)
time_options = ["1分钟", "2分钟", "3分钟", "4分钟", "5分钟"]
time_menu = ttk.Combobox(selection_frame, textvariable=time_var, values=time_options, state="readonly")
time_menu.grid(row=2, column=1, padx=5, pady=5)

start_button = tk.Button(selection_frame, text="开始游戏", 
                         command=lambda: start_game(p1_var.get(), p2_var.get(), int(time_var.get()[0]) * 60, root, selection_frame))
start_button.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()