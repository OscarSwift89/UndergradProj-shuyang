import tkinter as tk
from tkinter import ttk
import time
import tracemalloc
import psutil
import os
import numpy as np

from game import Game  # 注意：请确保 game.py 顶部已添加 "from board import Board"
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI

class GameGUI:
    def __init__(self, root, p1_ai, p2_ai, p3_ai, p4_ai, game_duration):
        self.root = root
        self.game_duration = game_duration  # 游戏总时长（秒）

        #定义棋子颜色与目标区域颜色的映射
        self.piece_colors = {1: "red", 2: "blue", 3: "green", 4: "magenta"}
        self.target_colors = {1: "lightcoral", 2: "khaki", 3: "lightgreen", 4: "skyblue"}

        # 创建 Canvas 绘制棋盘
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        #先保存各个agent，方便显示在信息栏
        self.agents = {1: p1_ai, 2: p2_ai, 3: p3_ai, 4: p4_ai,}

        # 信息面板放在右侧，针对4个玩家展示信息
        self.info_frame = tk.Frame(root)
        self.info_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)
        self.create_info_panel()

        # 创建游戏实例（修改后的Game支持4玩家）
        self.game = Game(p1_ai, p2_ai, p3_ai, p4_ai)
        self.cell_size = 600 // 12

        

        # 记录每个玩家决策的统计信息（此处仅示例，可根据实际扩展）
        self.stats = {i: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0} for i in range(1, 5)}
        self.start_time = time.perf_counter()
        self.process = psutil.Process(os.getpid())

        self.update_board()
        self.root.after(1000, self.game_step)

    def create_info_panel(self):
        # 每个玩家单独的信息区域
        self.info_labels = {}
        for player in range(1, 5):
            frame = tk.LabelFrame(self.info_frame, text=f"玩家 {player} 信息", padx=5, pady=5)
            frame.pack(fill="x", pady=5)
            self.info_labels[player] = {}

            #添加算法名称
            self.info_labels[player]['algorithm'] = tk.Label(frame, text= "算法： " + self.agents[player].__class__.__name__)
            self.info_labels[player]['algorithm'].pack(anchor= "w")
            #显示棋子颜色
            self.info_labels[player]['piece_color'] = tk.Label(frame, text= "棋子颜色： " + self.piece_colors[player])
            self.info_labels[player]['piece_color'].pack(anchor= "w")
            #显示目标区域颜色
            self.info_labels[player]['target_color'] = tk.Label(frame, text= "目标区域颜色： " + self.target_colors[player])
            self.info_labels[player]['target_color'].pack(anchor= "w")

            #现有显示信息
            self.info_labels[player]['current_time'] = tk.Label(frame, text="当前决策耗时: -")
            self.info_labels[player]['current_time'].pack(anchor="w")
            self.info_labels[player]['cumulative_time'] = tk.Label(frame, text="累计决策耗时: -")
            self.info_labels[player]['cumulative_time'].pack(anchor="w")
            self.info_labels[player]['decision_count'] = tk.Label(frame, text="决策次数: -")
            self.info_labels[player]['decision_count'].pack(anchor="w")
            self.info_labels[player]['latest_mem'] = tk.Label(frame, text="最新决策内存: -")
            self.info_labels[player]['latest_mem'].pack(anchor="w")

        # 总内存和游戏运行时间
        self.total_mem_label = tk.Label(self.info_frame, text="总内存消耗: -")
        self.total_mem_label.pack(anchor="w", pady=(10, 0))
        self.elapsed_label = tk.Label(self.info_frame, text="游戏运行时间: -")
        self.elapsed_label.pack(anchor="w", pady=(0, 10))
        # 分数显示（4个玩家的得分）
        self.score_label = tk.Label(self.info_frame, text="分数 - 玩家1: 0, 玩家2: 0, 玩家3: 0, 玩家4: 0", font=("Arial", 12, "bold"))
        self.score_label.pack(anchor="w", pady=(10, 0))

    def update_info_panel(self, elapsed, total_mem):
        for player in range(1, 5):
            cur = self.stats[player]
            self.info_labels[player]['current_time'].config(text=f"当前决策耗时: {cur['decision_time']*1000:.1f} ms")
            self.info_labels[player]['cumulative_time'].config(text=f"累计决策耗时: {cur['cumulative_time']:.2f} s")
            self.info_labels[player]['decision_count'].config(text=f"决策次数: {cur['decision_count']}")
            self.info_labels[player]['latest_mem'].config(text=f"最新决策内存: {cur['latest_mem'] / 1024:.1f} KB")
        self.total_mem_label.config(text=f"总内存消耗: {total_mem / (1024*1024):.1f} MB")
        self.elapsed_label.config(text=f"游戏运行时间: {elapsed:.1f} s")
        
        # 更新分数：各玩家的分数对应各自目标区域内的棋子数
        board = self.game.board.board
        p1_score = np.count_nonzero(board[9:12, 9:12] == 1)
        p2_score = np.count_nonzero(board[9:12, 0:3] == 2)
        p3_score = np.count_nonzero(board[0:3, 9:12] == 3)
        p4_score = np.count_nonzero(board[0:3, 0:3] == 4)
        self.score_label.config(text=f"分数 - 玩家1: {p1_score}, 玩家2: {p2_score}, 玩家3: {p3_score}, 玩家4: {p4_score}")

    def update_board(self):
        self.canvas.delete("all")
        board = self.game.board.board
        for i in range(12):
            for j in range(12):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                # 根据区域设定不同背景色（示例中）
                if i < 3 and j < 3:
                    fill_color = "skyblue"       # 左上：玩家4目标区域
                elif i < 3 and j >= 9:
                    fill_color = "lightgreen"    # 右上：玩家3目标区域
                elif i >= 9 and j < 3:
                    fill_color = "khaki"         # 左下：玩家2目标区域
                elif i >= 9 and j >= 9:
                    fill_color = "lightcoral"    # 右下：玩家1目标区域
                else:
                    fill_color = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                
                # 绘制棋子，根据棋子编号使用不同颜色
                if board[i, j] == 1:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="red")
                elif board[i, j] == 2:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="blue")
                elif board[i, j] == 3:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="green")
                elif board[i, j] == 4:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="magenta")

    def game_step(self):
        elapsed = time.perf_counter() - self.start_time
        total_mem = self.process.memory_info().rss
        
        if elapsed >= self.game_duration:
            # 统计得分并显示胜利信息
            board = self.game.board.board
            p1_score = np.count_nonzero(board[9:12,9:12] == 1)  # 玩家1在右下角
            p2_score = np.count_nonzero(board[9:12,0:3] == 2)   # 玩家2在左下角
            p3_score = np.count_nonzero(board[0:3,9:12] == 3)   # 玩家3在右上角
            p4_score = np.count_nonzero(board[0:3,0:3] == 4)    # 玩家4在左上角
            scores = {1: p1_score, 2: p2_score, 3: p3_score, 4: p4_score}
            winner = max(scores, key=scores.get)
            self.canvas.create_text(300, 300, text=f"玩家 {winner} 胜利", font=("Arial", 36, "bold"), fill="purple")
            return
        
        current_player = self.game.current_player
        current_ai = self.game.players[current_player]
        
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
        else:
            print(f"玩家 {current_player} 没有合法移动！")
        
        self.update_board()
        self.update_info_panel(elapsed, total_mem)
        self.game.current_player = (self.game.current_player % 4) + 1
        self.root.after(1000, self.game_step)

def start_game(p1_type, p2_type, p3_type, p4_type, game_duration, root, selection_frame):
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
    p3_ai = create_ai(p3_type, 3)
    p4_ai = create_ai(p4_type, 4)
    selection_frame.destroy()
    GameGUI(root, p1_ai, p2_ai, p3_ai, p4_ai, game_duration)

root = tk.Tk()
root.title("中国跳棋 AI 对战 - 4人对抗")
selection_frame = tk.Frame(root)
selection_frame.pack(padx=10, pady=10)

options = ["Greedy", "A* 算法", "MCTS", "Minimax"]

tk.Label(selection_frame, text="选择玩家1的AI:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家2的AI:").grid(row=1, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家3的AI:").grid(row=2, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家4的AI:").grid(row=3, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择游戏时长:").grid(row=4, column=0, padx=5, pady=5)

p1_var = tk.StringVar(value="Greedy")
p2_var = tk.StringVar(value="Greedy")
p3_var = tk.StringVar(value="Greedy")
p4_var = tk.StringVar(value="Greedy")
time_var = tk.StringVar(value="1分钟")  # 默认1分钟

p1_menu = ttk.Combobox(selection_frame, textvariable=p1_var, values=options, state="readonly")
p1_menu.grid(row=0, column=1, padx=5, pady=5)
p2_menu = ttk.Combobox(selection_frame, textvariable=p2_var, values=options, state="readonly")
p2_menu.grid(row=1, column=1, padx=5, pady=5)
p3_menu = ttk.Combobox(selection_frame, textvariable=p3_var, values=options, state="readonly")
p3_menu.grid(row=2, column=1, padx=5, pady=5)
p4_menu = ttk.Combobox(selection_frame, textvariable=p4_var, values=options, state="readonly")
p4_menu.grid(row=3, column=1, padx=5, pady=5)
time_options = ["1分钟", "2分钟", "3分钟", "4分钟", "5分钟"]
time_menu = ttk.Combobox(selection_frame, textvariable=time_var, values=time_options, state="readonly")
time_menu.grid(row=4, column=1, padx=5, pady=5)

start_button = tk.Button(selection_frame, text="开始游戏",
                         command=lambda: start_game(p1_var.get(), p2_var.get(), p3_var.get(), p4_var.get(),
                                                     int(time_var.get()[0]) * 60, root, selection_frame))
start_button.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
