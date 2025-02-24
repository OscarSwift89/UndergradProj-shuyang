import time
from board import Board

class Game:
    def __init__(self, player1_ai, player2_ai):
        self.board = Board()
        self.players = {1: player1_ai, 2: player2_ai}
        self.current_player = 1
        
    def run(self):
        print("游戏开始！")
        self.board.render()
        
        while not self.board.is_game_over():
            current_ai = self.players[self.current_player]
            print(f"玩家 {self.current_player} ({current_ai.__class__.__name__}) 的回合")
            
            move = current_ai.choose_move(self.board.board)
            if move:
                from_pos, to_pos = move
                print(f"移动棋子：{from_pos} -> {to_pos}")
                self.board.move_piece(from_pos, to_pos)
            else:
                print("没有合法移动！")
            
            self.board.render()
            time.sleep(1)
            self.current_player = 2 if self.current_player == 1 else 1
        
        print("游戏结束！")