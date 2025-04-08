import tkinter as tk
from tkinter import ttk
from game import Game
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI
from ai.bfs_ai import BFSAI

# 定义一个简单的 GUI 游戏类，用画布显示棋盘
class GameGUI:
    def __init__(self, root, p1_ai, p2_ai):
        self.root = root
        self.canvas = tk.Canvas(root, width=600, height=600)
        self.canvas.pack()
        self.game = Game(p1_ai, p2_ai)
        self.cell_size = 600 // 17
        self.update_board()
        # 每隔1秒更新一步
        self.root.after(1000, self.game_step)

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
            move = current_ai.choose_move(self.game.board.board)
            if move:
                from_pos, to_pos = move
                self.game.board.move_piece(from_pos, to_pos)
            self.game.current_player = 2 if self.game.current_player == 1 else 1
            self.update_board()
            self.root.after(1000, self.game_step)
        else:
            print("游戏结束！")

def start_game(p1_type, p2_type, root, selection_frame):
    # 根据选择的 AI 类型创建对应的 AI 实例
    def create_ai(ai_type, player_id):
        if ai_type == "Greedy":
            return GreedyAI(player_id)
        elif ai_type == "A* 算法":
            return AStarAI(player_id)
        elif ai_type == "MCTS":
            return MCTSAI(player_id)
        elif ai_type == "Minimax":
            return MinimaxAI(player_id)
        elif ai_type == "BFS":
            return BFSAI(player_id)
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

# 五个 AI 选项
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
