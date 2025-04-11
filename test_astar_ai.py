from board import Board
from ai.astar_ai import AStarAI

def test_astar_ai():
    board = Board()
    ai = AStarAI(1)
    move = ai.choose_move(board.board)
    print("AStarAI chose move:", move)

if __name__ == "__main__":
    test_astar_ai()