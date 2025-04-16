#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import psutil
import os
import numpy as np
import random
import tracemalloc

# 为加快模拟速度，不进行 sleep 延迟
time.sleep = lambda x: None

# 导入棋盘和 AI 模块（请确保你的项目结构与此对应）
from board import Board
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.mcts_ai import MCTSAI
from ai.minimax_ai import MinimaxAI

def simulate_game_with_stats(max_moves, agents):
    """
    模拟一局四人游戏，采用走子步数 max_moves 模拟游戏时长（例如 1分钟=60步）
    收集每个玩家的决策时间和内存峰值。
    
    返回一个字典，包含：
      'winner': 获胜玩家ID（以目标区域棋子数最多为胜）；
      'moves': 本局走步数；
      'stats': {player_id: {'times': [决策时间列表], 'mems': [内存峰值列表]}}
    """
    board_instance = Board()  # 初始棋盘（要求目标区域为空，采用对角起始布局）
    current_player = 1
    moves_count = 0
    process = psutil.Process(os.getpid())
    
    # 初始化各玩家统计数据
    stats = {1: {'times': [], 'mems': []},
             2: {'times': [], 'mems': []},
             3: {'times': [], 'mems': []},
             4: {'times': [], 'mems': []}}
    
    while moves_count < max_moves and not board_instance.is_game_over():
        agent = agents[current_player]
        # 使用 tracemalloc 记录本步内存峰值
        tracemalloc.start()
        start_time = time.time()
        move = agent.choose_move(board_instance.board)
        step_time = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # 记录当前玩家的决策时间与内存峰值
        stats[current_player]['times'].append(step_time)
        stats[current_player]['mems'].append(peak)
        
        # 如果找到了走法，则执行之
        if move:
            from_pos, to_pos = move
            board_instance.move_piece(from_pos, to_pos)
        # 否则直接换下一位
        moves_count += 1
        current_player = (current_player % 4) + 1
    
    # 判断胜者：统计各玩家在目标区域内的棋子数
    board_arr = board_instance.board
    p1_score = np.count_nonzero(board_arr[9:12, 9:12] == 1)    # 玩家1目标区域：右下
    p2_score = np.count_nonzero(board_arr[9:12, 0:3] == 2)       # 玩家2目标区域：左下
    p3_score = np.count_nonzero(board_arr[0:3, 9:12] == 3)       # 玩家3目标区域：右上
    p4_score = np.count_nonzero(board_arr[0:3, 0:3] == 4)        # 玩家4目标区域：左上
    scores = {1: p1_score, 2: p2_score, 3: p3_score, 4: p4_score}
    winner = max(scores, key=scores.get)
    
    return {'winner': winner, 'moves': moves_count, 'stats': stats}

def simulate_battles(time_limit_minutes, rounds=10):
    """
    针对指定游戏时长（分钟），进行 rounds 局模拟
    游戏时长以最大走步数计算（分钟 * 60）
    返回统计数据：每个算法的胜率、平均每步时间和平均每步内存使用。
    """
    max_moves = time_limit_minutes * 60
    print(f"\n开始模拟：游戏时长 {time_limit_minutes} 分钟（最多走 {max_moves} 步），共 {rounds} 局。")
    # 固定四个 agent 的组合：玩家1：Greedy；玩家2：A*；玩家3：MCTS；玩家4：Minimax
    agents_template = {
        1: GreedyAI(1),
        2: AStarAI(2),
        3: MCTSAI(3),
        4: MinimaxAI(4)
    }
    # 用于统计结果：胜率、平均每步决策时间、平均内存使用（单位 MB）
    win_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    # 分别统计每个 agent累计的总决策时间和内存，以及步数
    total_times = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    total_mems = {1: 0, 2: 0, 3: 0, 4: 0}
    total_steps = {1: 0, 2: 0, 3: 0, 4: 0}
    
    for i in range(rounds):
        result = simulate_game_with_stats(max_moves, agents_template)
        win_counts[result['winner']] += 1
        stats = result['stats']
        for p in [1,2,3,4]:
            total_times[p] += sum(stats[p]['times'])
            total_mems[p] += sum(stats[p]['mems'])
            total_steps[p] += len(stats[p]['times'])
        print(f"局 {i+1:2d}: Winner={result['winner']}, Moves={result['moves']}")

    # 计算平均每步时间、平均每步内存（转换为 MB）
    avg_times = {p: (total_times[p] / total_steps[p] if total_steps[p] > 0 else 0) for p in [1,2,3,4]}
    avg_mems = {p: (total_mems[p] / total_steps[p] if total_steps[p] > 0 else 0) for p in [1,2,3,4]}
    win_rates = {p: (win_counts[p] / rounds * 100) for p in [1,2,3,4]}

    # 构造结果字典
    results = {
        'win_counts': win_counts,
        'win_rates': win_rates,
        'avg_times': avg_times,
        'avg_mems': avg_mems
    }
    return results

def print_results_table(time_limit_minutes, results):
    # 输出表格格式的模拟结果
    print("\n========================================")
    print(f"游戏时长：约 {time_limit_minutes} 分钟")
    print("每局共进行30局对战")
    print("------------------------------------------------")
    print(f"{'Algorithm':<12}{'Wins':>8}{'Win Rate':>10}{'Avg Time/Step(s)':>20}{'Avg Mem/Step(MB)':>22}")
    print("------------------------------------------------")
    # 固定算法对应：玩家1：Greedy, 玩家2：A*, 玩家3：MCTS, 玩家4：Minimax
    algo_names = {1: "Greedy", 2: "A star", 3: "MCTS", 4: "Minimax"}
    for p in [1,2,3,4]:
        wins = results['win_counts'][p]
        rate = results['win_rates'][p]
        avg_time = results['avg_times'][p]
        avg_mem = results['avg_mems'][p] / (1024*1024)  # 转 MB
        print(f"{algo_names[p]:<12}{wins:8d}{rate:9.1f}%{avg_time:20.3f}{avg_mem:22.2f}")
    print("========================================\n")

if __name__ == '__main__':
    # 通过命令行参数指定时长（1~5分钟），如果没有参数，则分别运行1至5分钟的模拟
    if len(sys.argv) >= 2:
        try:
            t = int(sys.argv[1])
            if t < 1 or t > 5:
                print("请输入 1 到 5 之间的整数作为游戏时长（分钟）的参数。")
                sys.exit(1)
            durations = [t]
        except ValueError:
            print("参数必须是整数。")
            sys.exit(1)
    else:
        durations = [1,2,3,4,5]
    
    rounds = 30
    for dur in durations:
        results = simulate_battles(dur, rounds)
        print_results_table(dur, results)
