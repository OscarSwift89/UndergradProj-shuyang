import tkinter as tk
from tkinter import ttk
from colorama import init
from game import Game
from ai.greedy_ai import GreedyAI
#from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
#from ai.minimax_ai import MinimaxAI 

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

# 根据选择创建 AI 实例并开始游戏
def start_game(p1_type, p2_type, root, selection_frame):
    if p1_type == "Greedy":
        p1_ai = GreedyAI(1)
    elif p1_type == "MCTS":
        p1_ai = MCTSAI(1)
    else:
        p1_ai = GreedyAI(1)
    if p2_type == "Greedy":
        p2_ai = GreedyAI(2)
    elif p2_type == "MCTS":
        p2_ai = MCTSAI(2)
    else:
        p2_ai = GreedyAI(2)
    selection_frame.destroy()  # 移除选择界面
    GameGUI(root, p1_ai, p2_ai)

# 主窗口及 AI 选择界面
root = tk.Tk()
root.title("中国跳棋AI对战")
selection_frame = tk.Frame(root)
selection_frame.pack(padx=10, pady=10)

tk.Label(selection_frame, text="选择玩家1的AI:").grid(row=0, column=0, padx=5, pady=5)
tk.Label(selection_frame, text="选择玩家2的AI:").grid(row=1, column=0, padx=5, pady=5)
p1_var = tk.StringVar(value="Greedy")
p2_var = tk.StringVar(value="Greedy")
p1_menu = ttk.Combobox(selection_frame, textvariable=p1_var, values=["Greedy", "MCTS"], state="readonly")
p1_menu.grid(row=0, column=1, padx=5, pady=5)
p2_menu = ttk.Combobox(selection_frame, textvariable=p2_var, values=["Greedy", "MCTS"], state="readonly")
p2_menu.grid(row=1, column=1, padx=5, pady=5)

start_button = tk.Button(selection_frame, text="开始游戏", 
                         command=lambda: start_game(p1_var.get(), p2_var.get(), root, selection_frame))
start_button.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()




























def select_ai(player_id):
    print(f"\n选择玩家 {player_id} 的AI类型：")
    print("1. 贪心算法")
    print("2. A*算法")
    print("3. 蒙特卡洛树搜索(MCTS)")
    print("4. Minimax算法")  # 添加这一行
    choice = input("请输入选项 (1/2/3/4): ")
    
    if choice == '1':
        return GreedyAI(player_id)
    elif choice == '2':
        return AStarAI(player_id)
    elif choice == '3':
        return MCTSAI(player_id)
    elif choice == '4':  # 添加这一行
        return MinimaxAI(player_id)
    else:
        print("无效输入，默认使用贪心算法")
        return GreedyAI(player_id)
if __name__ == "__main__":
    # 初始化colorama
    init(autoreset=True)
    
    print("===== 中国跳棋AI对战 =====")
    print("请选择第一个玩家的AI：")
    p1_ai = select_ai(1)
    print("\n请选择第二个玩家的AI：")
    p2_ai = select_ai(2)
    
    game = Game(p1_ai, p2_ai)
    game.run()