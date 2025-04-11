from board import Board
from ai.minimax_ai import MinimaxAI

def test_minimax_ai():
    board = Board()
    ai = MinimaxAI(1)
    move = ai.choose_move(board.board)
    print("AStarAI chose move:", move)

if __name__ == "__main__":
    test_minimax_ai()