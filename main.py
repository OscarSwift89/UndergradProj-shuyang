import tkinter as tk
from tkinter import ttk
import time
import tracemalloc
import psutil
import os

from game import Game
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI
#from ai.bfs_ai import BFSAI

class GameGUI:
    def __init__(self, root, p1_ai, p2_ai):
        self.root = root
        # 使用 grid 布局，左侧显示棋盘，右侧显示实时信息
        self.canvas = tk.Canvas(root, width=600, height=600, bg="white")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        # 信息面板
        self.info_frame = tk.Frame(root)
        self.info_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)
        self.create_info_panel()
        
        self.game = Game(p1_ai, p2_ai)
        self.cell_size = 600 // 17
        
        # 用于记录决策统计信息，分别针对玩家1和玩家2
        self.stats = {
            1: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0},
            2: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0}
        }
        self.start_time = time.perf_counter()
        self.process = psutil.Process(os.getpid())
        
        self.update_board()
        self.root.after(1000, self.game_step)

    def create_info_panel(self):
        # 创建两个子面板，分别显示红（玩家1）和蓝（玩家2）的信息
        self.info_labels = {}  # 保存标签引用
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
        
        # 总内存与游戏总运行时间统一显示在面板底部
        self.total_mem_label = tk.Label(self.info_frame, text="总内存消耗: -")
        self.total_mem_label.pack(anchor="w", pady=(10,0))
        self.elapsed_label = tk.Label(self.info_frame, text="游戏运行时间: -")
        self.elapsed_label.pack(anchor="w")

    def update_info_panel(self, elapsed, total_mem):
        # 更新信息面板内容
        for player in [1, 2]:
            cur = self.stats[player]
            self.info_labels[player]['current_time'].config(text=f"当前决策耗时: {cur['decision_time']*1000:.1f} ms")
            self.info_labels[player]['cumulative_time'].config(text=f"累计决策耗时: {cur['cumulative_time']:.2f} s")
            self.info_labels[player]['decision_count'].config(text=f"决策次数: {cur['decision_count']}")
            # 转换内存单位为 KB
            self.info_labels[player]['latest_mem'].config(text=f"最新决策内存: {cur['latest_mem'] / 1024:.1f} KB")
        
        # 总内存单位转换为 MB
        self.total_mem_label.config(text=f"总内存消耗: {total_mem / (1024*1024):.1f} MB")
        self.elapsed_label.config(text=f"游戏运行时间: {elapsed:.1f} s")

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
        
        # 在棋盘四个角添加边框（4x4 区域）
        # 顶部左侧：行 0~3, 列 0~3
        self.canvas.create_rectangle(0, 0, self.cell_size*4, self.cell_size*4,
                                     outline="purple", width=3)
        # 顶部右侧：行 0~3, 列 13~16
        self.canvas.create_rectangle(self.cell_size*13, 0, self.cell_size*17, self.cell_size*4,
                                     outline="orange", width=3)
        # 底部左侧：行 13~16, 列 0~3
        self.canvas.create_rectangle(0, self.cell_size*13, self.cell_size*4, self.cell_size*17,
                                     outline="cyan", width=3)
        # 底部右侧：行 13~16, 列 13~16
        self.canvas.create_rectangle(self.cell_size*13, self.cell_size*13, self.cell_size*17, self.cell_size*17,
                                     outline="magenta", width=3)


    def game_step(self):
        if not self.game.board.is_game_over():
            current_player = self.game.current_player
            current_ai = self.game.players[current_player]
            
            # 记录决策前状态，测量决策耗时与消耗内存
            tracemalloc.start()
            start = time.perf_counter()
            move = current_ai.choose_move(self.game.board.board)
            decision_time = time.perf_counter() - start
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # 更新当前决策的统计数据
            self.stats[current_player]['decision_time'] = decision_time
            self.stats[current_player]['cumulative_time'] += decision_time
            self.stats[current_player]['decision_count'] += 1
            self.stats[current_player]['latest_mem'] = peak_mem  # 单位字节

            # 获取当前总内存占用
            total_mem = self.process.memory_info().rss  # 字节单位
            elapsed = time.perf_counter() - self.start_time

            if move:
                from_pos, to_pos = move
                self.game.board.move_piece(from_pos, to_pos)
            
            # 更新右侧信息面板
            self.update_info_panel(elapsed, total_mem)
            # 切换玩家
            self.game.current_player = 2 if current_player == 1 else 1
            self.update_board()
            self.root.after(1000, self.game_step)
        else:
            print("游戏结束！")

def start_game(p1_type, p2_type, root, selection_frame):
    # 根据选择创建对应 AI 对象
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
    selection_frame.destroy()  # 移除选择界面
    GameGUI(root, p1_ai, p2_ai)

# 主窗口及 AI 选择界面
root = tk.Tk()
root.title("中国跳棋AI对战")
selection_frame = tk.Frame(root)
selection_frame.pack(padx=10, pady=10)

# 支持五种 AI 类型
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
