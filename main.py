import tkinter as tk
from tkinter import ttk
import time
import tracemalloc
import psutil
import os
import numpy as np

from game import Game  # 请确保 game.py 已修改为支持4玩家，并且初始布局已经合理调整
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI
from ai.bfs_ai import BFSAgent

class GameGUI:
    def __init__(self, root, p1_ai, p2_ai, p3_ai, p4_ai, game_duration):
        self.root = root
        self.game_duration = game_duration
        
        # 保存各个 agent 实例，方便显示其算法名称
        self.agents = {1: p1_ai, 2: p2_ai, 3: p3_ai, 4: p4_ai}
        self.game = Game(p1_ai, p2_ai, p3_ai, p4_ai)
        
        # 定义棋子颜色和目标区域颜色映射（与 update_board 中的绘制保持一致）
        self.piece_colors = {1: "red", 2: "blue", 3: "green", 4: "magenta"}
        self.target_colors = {1: "lightcoral", 2: "khaki", 3: "lightgreen", 4: "skyblue"}
        
        # 创建棋盘 Canvas（左侧区域）
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # 创建右侧信息区域，并将其放入一个滚动区域
        self.info_frame = tk.Frame(root)
        self.info_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)
        self.create_scrollable_info_panel()

        self.cell_size = 600 // 12
        # 记录每个玩家决策统计信息
        self.stats = {i: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0} for i in range(1,5)}
        self.start_time = time.perf_counter()
        self.process = psutil.Process(os.getpid())

        self.update_board()
        self.root.after(1000, self.game_step)

    def create_scrollable_info_panel(self):
        # 创建一个 canvas 用来实现滚动区域
        self.info_canvas = tk.Canvas(self.info_frame, width=300, height=600)
        self.info_scrollbar = tk.Scrollbar(self.info_frame, orient="vertical", command=self.info_canvas.yview)
        self.info_canvas.configure(yscrollcommand=self.info_scrollbar.set)
        self.info_scrollbar.pack(side="right", fill="y")
        self.info_canvas.pack(side="left", fill="both", expand=True)
        # 在 canvas 内创建一个 frame 作为实际容器
        self.inner_info_frame = tk.Frame(self.info_canvas)
        self.inner_info_frame.bind("<Configure>", lambda e: self.info_canvas.configure(scrollregion=self.info_canvas.bbox("all")))
        self.info_canvas.create_window((0,0), window=self.inner_info_frame, anchor="nw")
        
        self.create_info_panel()

    def create_info_panel(self):
        # 为每个玩家创建一块显示区域
        self.info_labels = {}
        self.player_frames = {}
        for player in range(1, 5):
            # 每个玩家单独的区域
            frame = tk.Frame(self.inner_info_frame, bd=2, relief="groove", padx=5, pady=5)
            frame.pack(fill="x", pady=5)
            self.player_frames[player] = frame
            # 第一行：【玩家号：算法 - 棋子颜色】
            header_text = f"玩家 {player}: {self.agents[player].__class__.__name__} - {self.piece_colors[player]}"
            header_label = tk.Label(frame, text=header_text, font=("Arial", 12, "bold"))
            header_label.pack(anchor="w")
            # 其他统计信息
            stat_labels = {}
            stat_labels['current_time'] = tk.Label(frame, text="当前决策耗时: -")
            stat_labels['current_time'].pack(anchor="w")
            stat_labels['cumulative_time'] = tk.Label(frame, text="累计决策耗时: -")
            stat_labels['cumulative_time'].pack(anchor="w")
            stat_labels['decision_count'] = tk.Label(frame, text="决策次数: -")
            stat_labels['decision_count'].pack(anchor="w")
            stat_labels['latest_mem'] = tk.Label(frame, text="最新决策内存: -")
            stat_labels['latest_mem'].pack(anchor="w")
            self.info_labels[player] = stat_labels    
        
        # 整体信息
        self.total_mem_label = tk.Label(self.inner_info_frame, text="总内存消耗: -")
        self.total_mem_label.pack(anchor="w", pady=(10,0))
        self.elapsed_label = tk.Label(self.inner_info_frame, text="游戏运行时间: -")
        self.elapsed_label.pack(anchor="w", pady=(0,10))
        # 修改分数显示为多行显示
        self.score_label = tk.Label(self.inner_info_frame, text="分数：\n玩家1: 0\n玩家2: 0\n玩家3: 0\n玩家4: 0", font=("Arial", 12, "bold"))
        self.score_label.pack(anchor="w", pady=(10,0))


    def update_info_panel(self, elapsed, total_mem):
        for player in range(1, 5):
            cur = self.stats[player]
            self.info_labels[player]['current_time'].config(text=f"当前决策耗时: {cur['decision_time']*1000:.1f} ms")
            self.info_labels[player]['cumulative_time'].config(text=f"累计决策耗时: {cur['cumulative_time']:.2f} s")
            self.info_labels[player]['decision_count'].config(text=f"决策次数: {cur['decision_count']}")
            self.info_labels[player]['latest_mem'].config(text=f"最新决策内存: {cur['latest_mem'] / 1024:.1f} KB")
        self.total_mem_label.config(text=f"总内存消耗: {total_mem / (1024*1024):.1f} MB")
        self.elapsed_label.config(text=f"游戏运行时间: {elapsed:.1f} s")
        
        # 将分数转换为多行文本显示
        board = self.game.board.board
        p1_score = np.count_nonzero(board[9:12, 9:12] == 1)    # 玩家1目标区域：右下
        p2_score = np.count_nonzero(board[9:12, 0:3] == 2)       # 玩家2目标区域：左下
        p3_score = np.count_nonzero(board[0:3, 9:12] == 3)       # 玩家3目标区域：右上
        p4_score = np.count_nonzero(board[0:3, 0:3] == 4)        # 玩家4目标区域：左上
        score_text = f"分数：\n玩家1: {p1_score}\n玩家2: {p2_score}\n玩家3: {p3_score}\n玩家4: {p4_score}"
        self.score_label.config(text=score_text)


    def update_board(self):
        self.canvas.delete("all")
        board = self.game.board.board
        for i in range(12):
            for j in range(12):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if i < 3 and j < 3:
                    fill_color = "skyblue"       # 玩家4目标区域：左上
                elif i < 3 and j >= 9:
                    fill_color = "lightgreen"    # 玩家3目标区域：右上
                elif i >= 9 and j < 3:
                    fill_color = "khaki"         # 玩家2目标区域：左下
                elif i >= 9 and j >= 9:
                    fill_color = "lightcoral"    # 玩家1目标区域：右下
                else:
                    fill_color = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                
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
            board = self.game.board.board
            p1_score = np.count_nonzero(board[9:12,9:12] == 1)
            p2_score = np.count_nonzero(board[9:12,0:3] == 2)
            p3_score = np.count_nonzero(board[0:3,9:12] == 3)
            p4_score = np.count_nonzero(board[0:3,0:3] == 4)
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
        if ai_type == "BFS":
            return BFSAgent(player_id)
        else:
            return GreedyAI(player_id)
        
    p1_ai = create_ai(p1_type, 1)
    p2_ai = create_ai(p2_type, 2)
    p3_ai = create_ai(p3_type, 3)
    p4_ai = create_ai(p4_type, 4)
    selection_frame.destroy()
    GameGUI(root, p1_ai, p2_ai, p3_ai, p4_ai, game_duration)

root = tk.Tk()
root.title("ChineseChecker - AI.ver")
selection_frame = tk.Frame(root)
selection_frame.pack(padx=10, pady=10)

options = ["Greedy", "AStar", "MCTS", "Minimax", "BFS"]

tk.Label(selection_frame, text="选择玩家1的AI:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家2的AI:").grid(row=1, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家3的AI:").grid(row=2, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家4的AI:").grid(row=3, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择游戏时长:").grid(row=4, column=0, padx=5, pady=5)

p1_var = tk.StringVar(value="Greedy")
p2_var = tk.StringVar(value="Greedy")
p3_var = tk.StringVar(value="Greedy")
p4_var = tk.StringVar(value="Greedy")
time_var = tk.StringVar(value="1分钟")

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
