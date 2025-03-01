from board import Board

def test_board_initialization():
    """测试棋盘初始化"""
    print("===== 测试棋盘初始化 =====")
    board = Board()
    print("预期输出：玩家1的棋子位于左上角，玩家2的棋子位于右下角。")
    board.render()
    print("测试通过！\n")

def test_move_piece():
    """测试棋子移动"""
    print("===== 测试棋子移动 =====")
    board = Board()
    print("初始棋盘：")
    board.render()

    # 移动玩家1的棋子
    print("移动玩家1的棋子：(0, 0) -> (1, 0)")
    if board.move_piece((0, 0), (1, 0)):
        print("移动成功！")
    else:
        print("移动失败！")
    board.render()

    # 移动玩家2的棋子
    print("移动玩家2的棋子：(16, 16) -> (15, 16)")
    if board.move_piece((16, 16), (15, 16)):
        print("移动成功！")
    else:
        print("移动失败！")
    board.render()

    # 尝试移动到非法位置
    print("尝试移动到非法位置：(1, 0) -> (2, 0)（目标位置已被占用）")
    if board.move_piece((1, 0), (2, 0)):
        print("移动成功！")
    else:
        print("移动失败！")
    board.render()

    print("测试通过！\n")

def test_get_valid_moves():
    """测试合法移动检查"""
    print("===== 测试合法移动检查 =====")
    board = Board()
    print("初始棋盘：")
    board.render()

    # 检查玩家1的棋子 (0, 0) 的合法移动
    print("检查玩家1的棋子 (0, 0) 的合法移动：")
    moves = board.get_valid_moves((0, 0))
    print("合法移动：", moves)

    # 检查玩家2的棋子 (16, 16) 的合法移动
    print("检查玩家2的棋子 (16, 16) 的合法移动：")
    moves = board.get_valid_moves((16, 16))
    print("合法移动：", moves)

    print("测试通过！\n")

def test_jump_moves():
    """测试跳跃移动"""
    print("===== 测试跳跃移动 =====")
    board = Board()
    print("初始棋盘：")
    board.render()

    # 设置一个跳跃场景
    board.move_piece((0, 0), (1, 0))  # 移动玩家1的棋子
    board.move_piece((1, 0), (2, 0))  # 再次移动
    print("设置跳跃场景后的棋盘：")
    board.render()

    # 检查玩家1的棋子 (2, 0) 的跳跃移动
    print("检查玩家1的棋子 (2, 0) 的跳跃移动：")
    jumps = board.get_jump_moves((2, 0))
    print("跳跃移动：", jumps)

    print("测试通过！\n")

if __name__ == "__main__":
    # 运行所有测试
    test_board_initialization()
    test_move_piece()
    test_get_valid_moves()
    test_jump_moves()
    print("所有测试完成！")