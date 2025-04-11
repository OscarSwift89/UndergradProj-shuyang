from board import Board
from ai.greedy_ai import GreedyAI

def test_greedy_ai():
    board = Board()
    ai = GreedyAI(1)
    move = ai.choose_move(board.board)
    print("chose move:", move)

if __name__ == "__main__":
    test_greedy_ai()