from colorama import init
from game import Game
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI  # 添加这一行

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